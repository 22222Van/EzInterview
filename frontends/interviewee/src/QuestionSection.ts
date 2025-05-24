import QuestionDisplay from './QuestionViews/QuestionDisplay.vue'
import QuestionPreparing from './QuestionViews/QuestionPreparing.vue'
import { getSocket } from '@/socket'

import { defineComponent } from 'vue'

export default defineComponent({
  name: 'QuestionSection',
  data() {
    return {
      connectionStatus: 'connecting' as 'connecting' | 'connected' | 'error',
      mode: '' as '' | 'preparing' | 'waiting' | 'counting' | 'interviewing' | 'finished',
      questionContent: '',
      queueCount: 0,
      queueQuestionCount: 0,
      questionTitles: ['Q1', 'Q2'],
      currentQuestion: -1,
    }
  },
  computed: {
    questionCount(): number {
      return this.questionTitles.length
    },
  },
  components: {
    QuestionPreparing,
    QuestionDisplay,
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
        } else if (data.type === 'question' && typeof data.content === 'string') {
          this.mode = 'interviewing'
          this.questionContent = data.content
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
    }
  },
})
