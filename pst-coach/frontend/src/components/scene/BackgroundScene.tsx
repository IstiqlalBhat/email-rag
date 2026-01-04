"use client";

import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';

const vertexShader = `
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const fragmentShader = `
  uniform float uTime;
  uniform vec3 uColor1; 
  uniform vec3 uColor2; 
  uniform vec3 uColor3; 
  varying vec2 vUv;

  float hash(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
  }

  float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
  }

  void main() {
    vec2 uv = vUv;
    float t = uTime * 0.1;
    
    // Richer, slower movement
    float n1 = noise(uv * 1.5 + t);
    float n2 = noise(uv * 3.0 - t * 0.5);
    
    // Mix Terracotta (Warm) and Mineral (Cool)
    vec3 mixBase = mix(uColor1, uColor2, n1);
    
    // Add Sand/Gold highlights
    float h = smoothstep(0.4, 0.6, n2);
    
    vec3 finalColor = mix(mixBase, uColor3, h * 0.5);
    
    // Add noise grain for texture
    float grain = hash(uv * 100.0 + t) * 0.03;
    finalColor += grain;

    gl_FragColor = vec4(finalColor, 1.0);
  }
`;

function FluidPlane() {
    const meshRef = useRef<THREE.Mesh>(null!);

    const uniforms = useMemo(() => ({
        uTime: { value: 0 },
        // Terra 100 (Warm Pinkish)
        uColor1: { value: new THREE.Color('#f2e8e5') },
        // Mineral 100 (Cool Blueish)
        uColor2: { value: new THREE.Color('#d9e2ec') },
        // Terra 300 (Darker Warm)
        uColor3: { value: new THREE.Color('#e0cec7') },
    }), []);

    useFrame((state) => {
        if (meshRef.current) {
            (meshRef.current.material as THREE.ShaderMaterial).uniforms.uTime.value = state.clock.getElapsedTime();
        }
    });

    return (
        <mesh ref={meshRef} position={[0, 0, -2]}>
            <planeGeometry args={[25, 25]} />
            <shaderMaterial
                vertexShader={vertexShader}
                fragmentShader={fragmentShader}
                uniforms={uniforms}
            />
        </mesh>
    );
}

export default function BackgroundScene() {
    return (
        <div className="fixed inset-0 z-0 opacity-60">
            <Canvas
                camera={{ position: [0, 0, 1] }}
                gl={{ antialias: true }}
            >
                <FluidPlane />
            </Canvas>
        </div>
    );
}
