"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { Environment, useGLTF, useTexture } from "@react-three/drei";
import { Suspense, useMemo, useRef } from "react";
import type { CSSProperties } from "react";
import * as THREE from "three";

interface CanModelProps {
  texture: string;
  index?: number;
  active?: boolean;
  compact?: boolean;
}

function CanModel({ texture, index = 0, active = true, compact = false }: CanModelProps) {
  const group = useRef<THREE.Group>(null);
  const gltf = useGLTF("/assets/can.glb");
  const sourceMap = useTexture(texture);
  const map = useMemo(() => {
    const cloned = sourceMap.clone();
    cloned.colorSpace = THREE.SRGBColorSpace;
    cloned.wrapS = THREE.RepeatWrapping;
    cloned.needsUpdate = true;
    return cloned;
  }, [sourceMap]);
  const scene = useMemo(() => gltf.scene.clone(true), [gltf.scene]);

  useMemo(() => {
    scene.traverse((child) => {
      if (!(child instanceof THREE.Mesh)) return;
      child.castShadow = true;
      child.receiveShadow = true;
      child.material = new THREE.MeshPhysicalMaterial({
        color: child.name === "Shell" ? 0xffffff : 0xb9b9b9,
        map: child.name === "Shell" ? map : null,
        metalness: 0.88,
        roughness: 0.24,
        clearcoat: 0.75,
        clearcoatRoughness: 0.16,
        envMapIntensity: 1.65,
      });
    });
  }, [map, scene]);

  useFrame((state, delta) => {
    if (!group.current) return;
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!reduceMotion) group.current.rotation.y += delta * (active ? 0.11 : 0.025);
    group.current.position.y = Math.sin(state.clock.elapsedTime * 0.72 + index) * (compact ? 0.025 : 0.07);
  });

  return (
    <group
      ref={group}
      position={[index * (compact ? 1.28 : 2.38), 0, Math.abs(index) * -0.45]}
      rotation={[-0.1, index * -0.12, index * 0.03]}
      scale={compact ? 1.08 : active ? 1.38 : 1.02}
    >
      <primitive object={scene} />
    </group>
  );
}

export function ProductStage({
  texture,
  sideTextures = [],
  packshot = false,
  className = "",
}: {
  texture: string;
  sideTextures?: string[];
  packshot?: boolean;
  className?: string;
}) {
  const textures = packshot ? sideTextures : [texture];

  return (
    <div className={`product-stage ${className}`} aria-hidden="true">
      <div className={`fallback-cans ${packshot ? "is-packshot" : ""}`}>
        {textures.map((item, index) => (
          <div
            className="fallback-can"
            key={`fallback-${item}-${index}`}
            style={{
              backgroundImage: `url(${item})`,
              "--can-index": String(index),
              "--can-count": String(textures.length),
            } as CSSProperties}
          >
            <span className="fallback-cap" />
            <span className="fallback-shade" />
          </div>
        ))}
      </div>
      <Canvas
        dpr={[1, 1.5]}
        camera={{ position: packshot ? [0, 1, 15] : [0, 0.45, 14], fov: packshot ? 31 : 26 }}
        gl={{ alpha: true, antialias: true, powerPreference: "high-performance" }}
      >
        <ambientLight intensity={0.6} />
        <spotLight position={[2, 6, 6]} intensity={110} angle={0.46} penumbra={1} />
        <spotLight position={[-4, -2, 5]} intensity={45} color="#a693ff" angle={0.5} penumbra={1} />
        <Suspense fallback={null}>
          {packshot ? (
            <group position={[-((textures.length - 1) * 1.28) / 2, 0, 0]} rotation={[0.05, 0, -0.14]}>
              {textures.map((item, index) => (
                <CanModel key={`${item}-${index}`} texture={item} index={index} compact active={false} />
              ))}
            </group>
          ) : (
            <group>
              {textures.map((item, index) => (
                <CanModel
                  key={`${item}-${index}`}
                  texture={item}
                  index={index - 1}
                  active={index === 1 || textures.length === 1}
                />
              ))}
            </group>
          )}
          <Environment preset="studio" />
        </Suspense>
      </Canvas>
    </div>
  );
}

useGLTF.preload("/assets/can.glb");
