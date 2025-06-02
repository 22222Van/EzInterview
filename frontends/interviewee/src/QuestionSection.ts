import QuestionPreparing from './QuestionViews/QuestionPreparing.vue'
import QuestionCounting from './QuestionViews/QuestionCounting.vue'
import QuestionInterviewing from './QuestionViews/QuestionInterviewing.vue'
import QuestionFinished from './QuestionViews/QuestionFinished.vue'
import { getSocket } from '@/socket'
import { COUNTDOWN_TOTAL_TIME } from '@/constants'

import { defineComponent } from 'vue'

export default defineComponent({
  name: 'QuestionSection',
  data() {
    return {
      connectionStatus: 'connecting' as 'connecting' | 'connected' | 'error',
      mode: '' as '' | 'preparing' | 'waiting' | 'counting' | 'interviewing' | 'finished',
      queueCount: 0,
      queueQuestionCount: 0,
      questionTitles: [],
      currentQuestion: -1,
      countdown: -1,
      countdownTimer: null as null | number,
      questionHint: '' as string,
    }
  },
  computed: {
    questionCount(): number {
      return this.questionTitles.length
    },
  },
  components: {
    QuestionPreparing,
    QuestionCounting,
    QuestionInterviewing,
    QuestionFinished,
  },
  mounted() {
    const socket = getSocket()

    socket.onopen = () => {
      console.log('WebSocket 已连接')
      this.connectionStatus = 'connected'
    }

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)

        if (data.type === '') {
          this.mode = ''
        } else if (
          data.type === 'preparing' &&
          Array.isArray(data.questionTitles) &&
          typeof data.queueCount === 'number' &&
          typeof data.queueQuestionCount === 'number'
        ) {
          this.mode = 'preparing'
          this.questionTitles = data.questionTitles
          this.queueCount = data.queueCount
          this.queueQuestionCount = data.queueQuestionCount
        } else if (
          data.type === 'waiting' &&
          Array.isArray(data.questionTitles) &&
          typeof data.queueCount === 'number' &&
          typeof data.queueQuestionCount === 'number'
        ) {
          this.mode = 'waiting'
          this.questionTitles = data.questionTitles
          this.queueCount = data.queueCount
          this.queueQuestionCount = data.queueQuestionCount
        } else if (data.type === 'counting') {
          if (this.mode !== 'counting') {
            this.mode = 'counting'
            this.countdown = COUNTDOWN_TOTAL_TIME

            if (this.countdownTimer) {
              clearInterval(this.countdownTimer)
            }

            this.countdownTimer = window.setInterval(() => {
              if (this.countdown > 0) {
                this.countdown--
              } else {
                clearInterval(this.countdownTimer!)
                this.countdownTimer = null
                socket.send(JSON.stringify({ type: 'start' }))
              }
            }, 1000)
          }
        } else if (
          data.type === 'interviewing' &&
          typeof data.currentQuestion === 'number' &&
          typeof data.questionHint == 'string' &&
          Array.isArray(data.questionTitles)
        ) {
          this.mode = 'interviewing'
          this.currentQuestion = data.currentQuestion
          this.questionHint = data.questionHint
          this.questionTitles = data.questionTitles
        } else if (data.type === 'finish') {
          this.mode = 'finished'
          this.currentQuestion = this.questionTitles.length
        } else {
          console.warn('未知数据格式', data)
        }
      } catch (e) {
        console.error('接收到非JSON格式数据:', event.data)
      }
    }

    socket.onerror = (error) => {
      console.error('WebSocket 错误:', error)
    }

    socket.onclose = () => {
      this.connectionStatus = 'error'
      if (this.countdownTimer) {
        clearInterval(this.countdownTimer)
        this.countdownTimer = null
      }
    }
  },
  beforeUnmount() {
    if (this.countdownTimer) {
      clearInterval(this.countdownTimer)
      this.countdownTimer = null
    }
  },
})
