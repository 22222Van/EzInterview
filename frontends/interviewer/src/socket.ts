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

const availableQuestions: Ref<number[]> = ref([]) // 用 ref 代替 reactive
const questionMains: Ref<string[]> = ref([])
const realCurrentQuestion: Ref<number> = ref(-1)
const showHint: Ref<boolean> = ref(false)

export function getAvailableQuestions(): Ref<number[]> {
  return availableQuestions
}
export function getQuestionMains(): Ref<string[]> {
  return questionMains
}
export function getRealCurrentQuestion(): Ref<number> {
  return realCurrentQuestion
}
export function setAvailableQuestions(newArr: number[]): void {
  availableQuestions.value = [...newArr]
}
export function setQuestionMains(newArr: string[]): void {
  questionMains.value = [...newArr]
}
export function setRealCurrentQuestion(n: number): void {
  realCurrentQuestion.value = n
}
export function getShowHint(): Ref<boolean> {
  return showHint
}
export function setShowHint(b: boolean): void {
  showHint.value = b
}
