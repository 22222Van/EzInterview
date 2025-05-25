import { INTERVIEWER_PORT } from '@/constants'

let socket: WebSocket | null = null

export function getSocket(): WebSocket {
  if (!socket || socket.readyState === WebSocket.CLOSED) {
    const host = window.location.hostname
    const port = INTERVIEWER_PORT
    socket = new WebSocket(`ws://${host}:${port}/`)
  }
  return socket
}
