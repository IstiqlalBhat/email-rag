'use client'

import { useEffect, useState, useRef, useCallback } from 'react'
import { Loader2, Users } from 'lucide-react'
import api from '@/lib/api'

interface NetworkGraphProps {
    uploadId: string
    onNodeClick?: (name: string) => void
}

interface Node {
    id: number
    name: string
    x?: number
    y?: number
    vx?: number
    vy?: number
}

interface Edge {
    source: number
    target: number
    weight: number
}

export default function NetworkGraph({ uploadId, onNodeClick }: NetworkGraphProps) {
    const [nodes, setNodes] = useState<Node[]>([])
    const [edges, setEdges] = useState<Edge[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [hoveredNode, setHoveredNode] = useState<number | null>(null)
    const svgRef = useRef<SVGSVGElement>(null)
    const animationRef = useRef<number | null>(null)

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true)
                const response = await api.get('/api/analytics/network', {
                    params: { upload_id: uploadId }
                })

                // Initialize nodes with random positions
                const initialNodes = (response.data.nodes || []).map((node: Node) => ({
                    ...node,
                    x: 200 + Math.random() * 200,
                    y: 150 + Math.random() * 100,
                    vx: 0,
                    vy: 0
                }))

                setNodes(initialNodes)
                setEdges(response.data.edges || [])
                setError(null)
            } catch (err: any) {
                setError('Failed to load network data')
                console.error('NetworkGraph fetch error:', err)
            } finally {
                setLoading(false)
            }
        }

        if (uploadId) {
            fetchData()
        }

        return () => {
            if (animationRef.current) {
                cancelAnimationFrame(animationRef.current)
            }
        }
    }, [uploadId])

    // Simple force simulation
    useEffect(() => {
        if (nodes.length === 0) return

        const width = 600
        const height = 300
        const centerX = width / 2
        const centerY = height / 2

        const simulate = () => {
            setNodes(prevNodes => {
                const newNodes = prevNodes.map(node => ({ ...node }))

                // Apply forces
                for (let i = 0; i < newNodes.length; i++) {
                    // Center attraction
                    const dx = centerX - (newNodes[i].x || 0)
                    const dy = centerY - (newNodes[i].y || 0)
                    newNodes[i].vx = (newNodes[i].vx || 0) + dx * 0.001
                    newNodes[i].vy = (newNodes[i].vy || 0) + dy * 0.001

                    // Repulsion from other nodes
                    for (let j = 0; j < newNodes.length; j++) {
                        if (i !== j) {
                            const rx = (newNodes[i].x || 0) - (newNodes[j].x || 0)
                            const ry = (newNodes[i].y || 0) - (newNodes[j].y || 0)
                            const dist = Math.sqrt(rx * rx + ry * ry) || 1
                            if (dist < 100) {
                                newNodes[i].vx = (newNodes[i].vx || 0) + (rx / dist) * 2
                                newNodes[i].vy = (newNodes[i].vy || 0) + (ry / dist) * 2
                            }
                        }
                    }

                    // Apply velocity with damping
                    newNodes[i].x = (newNodes[i].x || 0) + (newNodes[i].vx || 0) * 0.1
                    newNodes[i].y = (newNodes[i].y || 0) + (newNodes[i].vy || 0) * 0.1
                    newNodes[i].vx = (newNodes[i].vx || 0) * 0.9
                    newNodes[i].vy = (newNodes[i].vy || 0) * 0.9

                    // Bounds
                    newNodes[i].x = Math.max(40, Math.min(width - 40, newNodes[i].x || 0))
                    newNodes[i].y = Math.max(40, Math.min(height - 40, newNodes[i].y || 0))
                }

                return newNodes
            })

            animationRef.current = requestAnimationFrame(simulate)
        }

        // Run simulation for a limited time
        let frame = 0
        const maxFrames = 200
        const animateBrief = () => {
            if (frame < maxFrames) {
                simulate()
                frame++
                animationRef.current = requestAnimationFrame(animateBrief)
            }
        }

        animateBrief()

        return () => {
            if (animationRef.current) {
                cancelAnimationFrame(animationRef.current)
            }
        }
    }, [nodes.length])

    const handleNodeClick = useCallback((node: Node) => {
        if (onNodeClick) {
            onNodeClick(node.name)
        }
    }, [onNodeClick])

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64 bg-white/40 rounded-2xl">
                <Loader2 className="w-8 h-8 text-terra-500 animate-spin" />
            </div>
        )
    }

    if (error || nodes.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-64 bg-white/40 rounded-2xl">
                <Users className="w-12 h-12 text-mineral-300 mb-4" />
                <p className="text-mineral-500">
                    {error || 'No relationship data available yet'}
                </p>
            </div>
        )
    }

    return (
        <div className="bg-white/60 backdrop-blur-md rounded-2xl p-6 border border-white/50">
            <h3 className="text-lg font-semibold text-mineral-900 mb-4 flex items-center gap-2">
                <Users className="w-5 h-5 text-terra-600" />
                Email Connections
            </h3>

            <svg
                ref={svgRef}
                viewBox="0 0 600 300"
                className="w-full h-auto"
                style={{ minHeight: '300px' }}
            >
                {/* Edges */}
                {edges.map((edge, i) => {
                    const source = nodes[edge.source]
                    const target = nodes[edge.target]
                    if (!source || !target) return null

                    return (
                        <line
                            key={`edge-${i}`}
                            x1={source.x}
                            y1={source.y}
                            x2={target.x}
                            y2={target.y}
                            stroke="#C07A5C"
                            strokeWidth={Math.min(edge.weight, 4)}
                            strokeOpacity={0.4}
                        />
                    )
                })}

                {/* Nodes */}
                {nodes.map((node) => {
                    const isHovered = hoveredNode === node.id
                    const radius = isHovered ? 24 : 18

                    return (
                        <g
                            key={`node-${node.id}`}
                            onClick={() => handleNodeClick(node)}
                            onMouseEnter={() => setHoveredNode(node.id)}
                            onMouseLeave={() => setHoveredNode(null)}
                            className="cursor-pointer"
                        >
                            <circle
                                cx={node.x}
                                cy={node.y}
                                r={radius}
                                fill={isHovered ? '#C07A5C' : '#E8DDD3'}
                                stroke="#C07A5C"
                                strokeWidth={2}
                                className="transition-all duration-200"
                            />
                            <text
                                x={node.x}
                                y={(node.y || 0) + radius + 14}
                                textAnchor="middle"
                                className="text-xs fill-mineral-700 font-medium pointer-events-none"
                            >
                                {node.name.length > 10 ? node.name.slice(0, 10) + '...' : node.name}
                            </text>
                        </g>
                    )
                })}
            </svg>

            <p className="text-xs text-mineral-400 text-center mt-4">
                Click a node to see emails with this contact
            </p>
        </div>
    )
}
