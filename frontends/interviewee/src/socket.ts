let socket: WebSocket | null = null

export function getSocket(): WebSocket {
  if (!socket || socket.readyState === WebSocket.CLOSED) {
    const host = window.location.hostname
    const port = '9009'
    socket = new WebSocket(`ws://${host}:${port}/`)
  }
  return socket
}
