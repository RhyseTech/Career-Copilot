'use client';

import { useEffect, useRef } from 'react';

export default function ThreeBackground() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    const container = containerRef.current;

    // Dynamically load Three.js from CDN to avoid SSR issues
    const script = document.createElement('script');
    script.src = 'https://ajax.googleapis.com/ajax/libs/threejs/r125/three.min.js';
    script.onload = () => initScene(container);
    document.head.appendChild(script);

    let animId: number;
    let renderer: any;

    function initScene(container: HTMLDivElement) {
      const THREE = (window as any).THREE;
      if (!THREE) return;

      const width = container.clientWidth || window.innerWidth;
      const height = container.clientHeight || window.innerHeight;

      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
      camera.position.z = 45;

      renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: 'high-performance' });
      renderer.setSize(width, height);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      container.appendChild(renderer.domElement);

      // Lighting
      const ambientLight = new THREE.AmbientLight(0x0a192f, 2.5);
      scene.add(ambientLight);
      const pointLight1 = new THREE.PointLight(0x6366f1, 4, 120);
      pointLight1.position.set(20, 20, 25);
      scene.add(pointLight1);
      const pointLight2 = new THREE.PointLight(0x00f0ff, 3, 100);
      pointLight2.position.set(-25, -15, 20);
      scene.add(pointLight2);

      // Wave plane
      const planeGeo = new THREE.PlaneGeometry(90, 60, 48, 36);
      const planeMat = new THREE.MeshStandardMaterial({
        color: 0x1e293b, wireframe: true, roughness: 0.2, metalness: 0.85,
        transparent: true, opacity: 0.18,
      });
      const wirePlane = new THREE.Mesh(planeGeo, planeMat);
      wirePlane.rotation.x = -Math.PI / 2.8;
      wirePlane.position.y = -12;
      wirePlane.position.z = -5;
      scene.add(wirePlane);

      // Floating icosahedron nodes
      const nodeGroup = new THREE.Group();
      const nodeGeo = new THREE.IcosahedronGeometry(1.2, 0);
      const nodeMat = new THREE.MeshPhongMaterial({
        color: 0x00f0ff, emissive: 0x4f46e5, emissiveIntensity: 0.6,
        shininess: 90, wireframe: true, transparent: true, opacity: 0.45,
      });
      const nodes: any[] = [];
      for (let i = 0; i < 18; i++) {
        const mesh = new THREE.Mesh(nodeGeo, nodeMat);
        mesh.position.set(
          (Math.random() - 0.5) * 80,
          (Math.random() - 0.5) * 45,
          (Math.random() - 0.5) * 25,
        );
        mesh.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, 0);
        const scale = 0.5 + Math.random() * 0.8;
        mesh.scale.set(scale, scale, scale);
        mesh.userData = {
          rotSpeedX: (Math.random() - 0.5) * 0.02,
          rotSpeedY: (Math.random() - 0.5) * 0.02,
          baseY: mesh.position.y,
          phase: Math.random() * Math.PI * 2,
        };
        nodeGroup.add(mesh);
        nodes.push(mesh);
      }
      scene.add(nodeGroup);

      // Particles
      const particleCount = 280;
      const pGeometry = new THREE.BufferGeometry();
      const pPositions = new Float32Array(particleCount * 3);
      for (let i = 0; i < particleCount; i++) {
        pPositions[i * 3] = (Math.random() - 0.5) * 110;
        pPositions[i * 3 + 1] = (Math.random() - 0.5) * 70;
        pPositions[i * 3 + 2] = (Math.random() - 0.5) * 40;
      }
      pGeometry.setAttribute('position', new THREE.BufferAttribute(pPositions, 3));

      const canvas2d = document.createElement('canvas');
      canvas2d.width = 32; canvas2d.height = 32;
      const ctx = canvas2d.getContext('2d')!;
      const grad = ctx.createRadialGradient(16, 16, 0, 16, 16, 16);
      grad.addColorStop(0, 'rgba(0,240,255,1)');
      grad.addColorStop(0.35, 'rgba(99,102,241,0.6)');
      grad.addColorStop(1, 'rgba(15,23,42,0)');
      ctx.fillStyle = grad;
      ctx.beginPath(); ctx.arc(16, 16, 16, 0, Math.PI * 2); ctx.fill();

      const pMaterial = new THREE.PointsMaterial({
        size: 1.8, map: new THREE.CanvasTexture(canvas2d),
        transparent: true, opacity: 0.55,
        blending: THREE.AdditiveBlending, depthWrite: false,
      });
      const particles = new THREE.Points(pGeometry, pMaterial);
      scene.add(particles);

      // Mouse
      let targetX = 0, targetY = 0, mouseX = 0, mouseY = 0;
      const onMouseMove = (e: MouseEvent) => {
        targetX = ((e.clientX / window.innerWidth) * 2 - 1) * 4;
        targetY = (-(e.clientY / window.innerHeight) * 2 + 1) * 3;
      };
      window.addEventListener('mousemove', onMouseMove);

      const onResize = () => {
        const w = container.clientWidth || window.innerWidth;
        const h = container.clientHeight || window.innerHeight;
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        renderer.setSize(w, h);
      };
      window.addEventListener('resize', onResize);

      // Animate
      const clock = new THREE.Clock();
      const posAttr = planeGeo.attributes.position;
      const vCount = posAttr.count;

      function animate() {
        animId = requestAnimationFrame(animate);
        const t = clock.getElapsedTime();
        mouseX += (targetX - mouseX) * 0.05;
        mouseY += (targetY - mouseY) * 0.05;
        camera.position.x = mouseX;
        camera.position.y = mouseY;
        camera.lookAt(0, 0, 0);

        for (let i = 0; i < vCount; i++) {
          const u = posAttr.getX(i);
          const v = posAttr.getY(i);
          posAttr.setZ(i, Math.sin(u * 0.15 + t * 1.2) * Math.cos(v * 0.18 + t * 0.9) * 2.2);
        }
        posAttr.needsUpdate = true;

        nodes.forEach(node => {
          node.rotation.x += node.userData.rotSpeedX;
          node.rotation.y += node.userData.rotSpeedY;
          node.position.y = node.userData.baseY + Math.sin(t * 1.5 + node.userData.phase) * 1.2;
        });

        particles.rotation.y = t * 0.025;
        particles.rotation.x = Math.sin(t * 0.015) * 0.08;
        renderer.render(scene, camera);
      }
      animate();

      // Cleanup stored refs
      (container as any).__cleanup = () => {
        cancelAnimationFrame(animId);
        window.removeEventListener('mousemove', onMouseMove);
        window.removeEventListener('resize', onResize);
        if (renderer) renderer.dispose();
        if (container.contains(renderer.domElement)) container.removeChild(renderer.domElement);
      };
    }

    return () => {
      (container as any).__cleanup?.();
      if (script.parentNode) script.parentNode.removeChild(script);
    };
  }, []);

  return (
    <>
      {/* Three.js canvas container */}
      <div
        ref={containerRef}
        data-three-bg
        className="fixed inset-0 w-full h-full pointer-events-none z-0"
        aria-hidden="true"
      />
      {/* Ambient vignette overlay */}
      <div
        data-three-vignette
        className="fixed inset-0 pointer-events-none z-[1]"
        style={{
          background:
            'radial-gradient(circle at 50% 15%, rgba(99,102,241,0.08) 0%, rgba(7,10,19,0.75) 60%, rgba(7,10,19,0.96) 100%)',
        }}
        aria-hidden="true"
      />
    </>
  );
}
