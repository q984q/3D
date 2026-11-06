import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import {preparePavingUV,createPlantPreview} from '../src/lookdev.js';

test('paving UVs follow world meters and original geometry is unchanged',()=>{
 const source=new THREE.BufferGeometry();source.setAttribute('position',new THREE.Float32BufferAttribute([0,0,0,2,0,0,0,0,2],3));
 const mesh=new THREE.Mesh(source);mesh.position.set(10,0,-4);preparePavingUV(mesh,2);
 assert.notEqual(mesh.geometry,source);assert.equal(source.hasAttribute('uv'),false);
 assert.deepEqual(Array.from(mesh.geometry.getAttribute('uv').array),[5,-2,6,-2,5,-1]);
 assert.throws(()=>preparePavingUV(mesh,0));
});
test('preview plant fits marker center and is grounded without modifying template',()=>{
 const source=new THREE.Mesh(new THREE.BoxGeometry(2,4,1));source.position.set(1,2,-3);source.rotation.y=.5;source.updateMatrixWorld(true);
 const original=source.position.clone();const preview=createPlantPreview(source,new THREE.Vector3(10,99,-15),.68);preview.updateMatrixWorld(true);
 const bounds=new THREE.Box3().setFromObject(preview);const size=bounds.getSize(new THREE.Vector3()),center=bounds.getCenter(new THREE.Vector3());
 assert.ok(Math.max(size.x,size.z)<=.680001);assert.ok(Math.abs(center.x-10)<1e-6);assert.ok(Math.abs(center.z+15)<1e-6);assert.ok(Math.abs(bounds.min.y-.02)<1e-6);
 assert.ok(source.position.equals(original));
});
