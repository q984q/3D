import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
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
let model;
function setLayers(){if(!model)return;model.traverse(o=>{if(o.isMesh&&o.name.startsWith('REFERENCE_PDF'))o.visible=document.querySelector('#reference').checked;if(o.isMesh&&(o.name.startsWith('TREE_SYMBOL_')||o.name.startsWith('CENTRAL_PLANT_')))o.visible=document.querySelector('#trees').checked;if(o.isMesh&&o.name.startsWith('COURTYARD_PARTIAL_'))o.visible=document.querySelector('#field').checked;})}
for(const id of ['reference','trees','field'])document.getElementById(id).addEventListener('change',setLayers);
new GLTFLoader().load('/model/palladium_reconstruction_03.glb',g=>{model=g.scene;model.traverse(o=>{if(o.isMesh&&o.name.startsWith('REFERENCE_PDF'))o.material=new THREE.MeshBasicMaterial({map:o.material.map,side:THREE.DoubleSide});});scene.add(model);setLayers();status.remove()},undefined,e=>{console.error(e);status.textContent='Не удалось загрузить модель. Обновите страницу.'});
function resize(){const w=view.clientWidth,h=view.clientHeight;camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h)}window.addEventListener('resize',resize);
renderer.setAnimationLoop(()=>{controls.update();renderer.render(scene,camera)});
