import * as THREE from 'three';

/** Add world-aligned, illustrative UVs to a private geometry copy. */
export function preparePavingUV(mesh, repeatMeters = 2) {
  if (!(repeatMeters > 0)) throw new Error('repeatMeters must be positive');
  mesh.updateWorldMatrix(true, false);
  mesh.geometry = mesh.geometry.clone();
  const positions = mesh.geometry.getAttribute('position');
  const uv = new Float32Array(positions.count * 2);
  const v = new THREE.Vector3();
  for (let i = 0; i < positions.count; i++) {
    v.fromBufferAttribute(positions, i).applyMatrix4(mesh.matrixWorld);
    uv[2*i] = v.x / repeatMeters;
    uv[2*i+1] = v.z / repeatMeters;
  }
  mesh.geometry.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
}

/** Clone one of the source plants, fitting its footprint inside a circular marker. */
export function createPlantPreview(template, target, diameter = .68) {
  const box = new THREE.Box3().setFromObject(template);
  const size = box.getSize(new THREE.Vector3());
  const center = box.getCenter(new THREE.Vector3());
  const width = Math.max(size.x, size.z);
  if (!Number.isFinite(width) || width <= 0 || diameter <= 0) throw new Error('Invalid plant model bounds');
  const scale = diameter / width;
  const wrapper = new THREE.Group();
  const plant = template.clone(true);
  plant.scale.multiplyScalar(scale);
  plant.position.set((plant.position.x-center.x)*scale, (plant.position.y-box.min.y)*scale, (plant.position.z-center.z)*scale);
  wrapper.add(plant);
  wrapper.position.set(target.x, .02, target.z);
  return wrapper;
}
