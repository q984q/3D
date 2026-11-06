import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { createPlantPreview, preparePavingUV } from './lookdev.js';
import './style.css';
const view=document.querySelector('#viewport'), status=document.querySelector('#status');
const renderer=new THREE.WebGLRenderer({antialias:true});
renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
renderer.setSize(view.clientWidth,view.clientHeight);
renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.setClearColor(0xcad3d3);view.appendChild(renderer.domElement);
const scene=new THREE.Scene();const camera=new THREE.PerspectiveCamera(38,view.clientWidth/view.clientHeight,.1,1500);
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.minDistance=5;controls.maxDistance=500;controls.maxPolarAngle=Math.PI/2-.01;
scene.add(new THREE.HemisphereLight(0xffffff,0x9ca5a3,2));const sun=new THREE.DirectionalLight(0xffffff,2);sun.position.set(-50,130,40);scene.add(sun);
const presets={
 axon:{eye:[160,115,90],target:[63,0,-44.6]},top:{eye:[63,230,-44.59],target:[63,0,-44.6]},
 courtyard:{eye:[62,55,-125],target:[62,0,-68]},playground:{eye:[20,37,-100],target:[34,0,-68]},
 centre:{eye:[79,35,-103],target:[53.5,0,-62]},shevchenko:{eye:[62,35,38],target:[62,0,-19]},sharipova:{eye:[154,32,-42],target:[105,0,-42]}
};
function preset(name){const p=presets[name];controls.target.set(...p.target);camera.position.set(...p.eye);camera.lookAt(controls.target);controls.update();document.querySelectorAll('.buttons button').forEach(b=>b.classList.toggle('active',b.id===name))}
for(const name of Object.keys(presets))document.getElementById(name).onclick=()=>preset(name);
preset('axon');
let model, detailedPlants, pavingMaterial;
let plantPromise, pavingPromise;
const originals=new Map();
const checked=id=>document.getElementById(id).checked;
function notify(text){status.textContent=text;status.hidden=!text;}
function setLayers(){
 if(!model)return;
 const showPlants=checked('trees'), detailsReady=checked('realPlants') && !!detailedPlants;
 model.traverse(o=>{
  if(!o.isMesh)return;
  if(o.name.startsWith('REFERENCE_PDF'))o.visible=checked('reference');
  if(o.name.startsWith('TREE_SYMBOL_'))o.visible=showPlants;
  if(o.name.startsWith('CENTRAL_PLANT_'))o.visible=showPlants && !detailsReady;
  if(o.name.startsWith('COURTYARD_PARTIAL_'))o.visible=checked('field');
  if(o.name.startsWith('CENTRAL_PAVING_') && originals.has(o)) o.material=checked('realPaving') && pavingMaterial ? pavingMaterial : originals.get(o);
 });
 if(detailedPlants)detailedPlants.visible=showPlants && detailsReady;
}
for(const id of ['reference','trees','field'])document.getElementById(id).addEventListener('change',setLayers);
function loadPlants(){
 if(plantPromise)return plantPromise;
 plantPromise=new GLTFLoader().loadAsync('/assets/polyhaven/shrub_02.glb').then(g=>{
  // The source GLB is a cluster of four bushes. Use just its first component.
  const template=g.scene.children[0];
  if(!template)throw new Error('Plant asset has no component');
  const group=new THREE.Group();group.name='PREVIEW_ONLY_NINE_UNCONFIRMED_PLANTS';
  const centers=[];
  model.updateMatrixWorld(true);
  model.traverse(o=>{
   if(o.isMesh&&o.name.startsWith('CENTRAL_PLANT_'))centers.push(new THREE.Box3().setFromObject(o).getCenter(new THREE.Vector3()));
  });
  if(centers.length!==9)throw new Error('Expected nine central plant markers');
  for(const pos of centers)group.add(createPlantPreview(template,pos));
  scene.add(group);detailedPlants=group;setLayers();
 }).catch(e=>{plantPromise=undefined;throw e});
 return plantPromise;
}
function loadPaving(){
 if(pavingPromise)return pavingPromise;
 const loader=new THREE.TextureLoader();
 pavingPromise=Promise.all(['Color','Normal','Roughness'].map(c=>loader.loadAsync(`/assets/ambientcg/PavingStones002_${c}_1k.jpg`))).then(([color,normal,rough])=>{
  color.colorSpace=THREE.SRGBColorSpace;
  for(const tex of [color,normal,rough]){tex.wrapS=tex.wrapT=THREE.RepeatWrapping;tex.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());}
  pavingMaterial=new THREE.MeshStandardMaterial({map:color,normalMap:normal,normalScale:new THREE.Vector2(.35,.35),roughnessMap:rough,roughness:1,metalness:0});
  model.updateMatrixWorld(true);
  model.traverse(o=>{if(o.isMesh && o.name.startsWith('CENTRAL_PAVING_')){originals.set(o,o.material);preparePavingUV(o,2);}});
  if(!originals.size)throw new Error('No central paving geometry');
  setLayers();
 }).catch(e=>{pavingPromise=undefined;throw e});
 return pavingPromise;
}
async function handlePreview(id,load){
 if(!checked(id)){setLayers();return}
 if(!model){document.getElementById(id).checked=false;notify('Дождитесь загрузки основной модели.');return}
 notify('Загрузка пробных материалов…');
 try{await load();notify('');setLayers()}
 catch(e){console.error(e);document.getElementById(id).checked=false;setLayers();notify('Не удалось загрузить тестовый материал. Попробуйте снова.')}
}
document.getElementById('realPlants').addEventListener('change',()=>handlePreview('realPlants',loadPlants));
document.getElementById('realPaving').addEventListener('change',()=>handlePreview('realPaving',loadPaving));
new GLTFLoader().load('/model/palladium_reconstruction_03.glb',g=>{
 model=g.scene;model.traverse(o=>{if(o.isMesh&&o.name.startsWith('REFERENCE_PDF'))o.material=new THREE.MeshBasicMaterial({map:o.material.map,side:THREE.DoubleSide});});
 scene.add(model);setLayers();notify('');
},undefined,e=>{console.error(e);notify('Не удалось загрузить модель. Обновите страницу.')});
function resize(){const w=view.clientWidth,h=view.clientHeight;camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h)}window.addEventListener('resize',resize);
renderer.setAnimationLoop(()=>{controls.update();renderer.render(scene,camera)});
