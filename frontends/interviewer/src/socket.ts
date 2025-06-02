import { INTERVIEWER_PORT } from '@/constants'
import { reactive, ref } from 'vue'
import type { Ref } from 'vue'

let socket: WebSocket | null = null

export function getSocket(): WebSocket {
  if (!socket || socket.readyState === WebSocket.CLOSED) {
    const host = window.location.hostname
    const port = INTERVIEWER_PORT
    socket = new WebSocket(`ws://${host}:${port}/`)
  }
  return socket
}

const availableQuestions = reactive<number[]>([])
const questionMains = reactive<string[]>([])
const realCurrentQuestion = ref<number>(-1)

export function getAvailableQuestions(): number[] {
  return availableQuestions
}

export function getQuestionMains(): string[] {
  return questionMains
}

export function getRealCurrentQuestion(): Ref<number> {
  return realCurrentQuestion
}

export function setAvailableQuestions(newArr: number[]): void {
  availableQuestions.splice(0, availableQuestions.length, ...newArr)
}

export function setQuestionMains(newArr: string[]): void {
  questionMains.splice(0, questionMains.length, ...newArr)
}

export function setRealCurrentQuestion(n: number): void {
  realCurrentQuestion.value = n
}
