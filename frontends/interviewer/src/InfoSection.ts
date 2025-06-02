import { defineComponent, ref, watch } from 'vue'
import {
  getSocket,
  getAvailableQuestions,
  getQuestionMains,
  getRealCurrentQuestion,
} from '@/socket'

interface Student {
  name: string
  id: string
}

const socket = getSocket()

export default defineComponent({
  name: 'InfoSection',
  data() {
    return {
      student: {
        name: '张伟',
        id: '2023123456',
      } as Student,
      avatarUrl: 'https://i.pravatar.cc/1000',
      volume: 50,
      micLevel: 70,
      networkQuality: '非常好',
      availableQuestions: getAvailableQuestions(),
      questionMains: getQuestionMains(),
      realCurrentQuestion: getRealCurrentQuestion(),
    }
  },
  methods: {
    sendChange() {
      socket.send(JSON.stringify({ type: 'select', selection: this.availableQuestions }))
    },
  },
})
