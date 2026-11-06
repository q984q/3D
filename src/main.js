import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import './style.css';
const view=document.querySelector('#viewport'), status=document.querySelector('#status');
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));renderer.setSize(view.clientWidth,view.clientHeight);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.setClearColor(0xcad3d3);view.appendChild(renderer.domElement);
const scene=new THREE.Scene();const camera=new THREE.PerspectiveCamera(38,view.clientWidth/view.clientHeight,.1,1500);
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.minDistance=10;controls.maxDistance=500;controls.maxPolarAngle=Math.PI/2-.01;
scene.add(new THREE.HemisphereLight(0xffffff,0x9ca5a3,2));const sun=new THREE.DirectionalLight(0xffffff,2);sun.position.set(-50,130,40);scene.add(sun);
const target=new THREE.Vector3(63,0,-44.6);
function preset(name){controls.target.copy(target);if(name==='top'){camera.position.set(63,230,-44.59)}else{camera.position.set(160,115,90)}camera.lookAt(target);controls.update();document.querySelectorAll('.buttons button').forEach(b=>b.classList.toggle('active',b.id===name))}
document.querySelector('#top').onclick=()=>preset('top');document.querySelector('#axon').onclick=()=>preset('axon');preset('axon');
new GLTFLoader().load('/model/palladium_reconstruction_01.glb',g=>{g.scene.traverse(o=>{if(o.isMesh&&o.name.includes('REFERENCE_PDF')){o.material=new THREE.MeshBasicMaterial({map:o.material.map,side:THREE.DoubleSide});}});scene.add(g.scene);status.remove()},undefined,e=>{console.error(e);status.textContent='Не удалось загрузить модель. Обновите страницу.'});
function resize(){const w=view.clientWidth,h=view.clientHeight;camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h)}window.addEventListener('resize',resize);
renderer.setAnimationLoop(()=>{controls.update();renderer.render(scene,camera)});
