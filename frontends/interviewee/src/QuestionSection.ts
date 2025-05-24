import QuestionDisplay from './QuestionViews/QuestionDisplay.vue'
import QuestionPreparing from './QuestionViews/QuestionPreparing.vue'

import { defineComponent } from 'vue'

export default defineComponent({
  name: 'QuestionSection',
  data() {
    return {
      connectionStatus: 'connecting' as 'connecting' | 'connected' | 'error',
      mode: 'preparing' as 'preparing' | 'waiting' | 'counting' | 'interviewing' | 'finished',
      questionContent: '',
      queueCount: 0,
      queueQuestionCount: 0,
      questionTitles: [],
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
    const host = window.location.hostname
    const port = '9009'
    const socket = new WebSocket(`ws://${host}:${port}/`)

    socket.onopen = () => {
      console.log('WebSocket 已连接')
      this.connectionStatus = 'connected'
    }

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)

        if (data.type === 'waiting' && typeof data.count === 'number') {
          this.mode = 'waiting'
          this.queueCount = data.count
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
