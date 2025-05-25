import QuestionDisplay from './QuestionViews/QuestionDisplay.vue'
import QuestionRejected from './QuestionViews/QuestionRejected.vue'
import QuestionIdle from './QuestionViews/QuestionIdle.vue'
import QuestionCounting from './QuestionViews/QuestionCounting.vue'
import { getSocket } from '@/socket'

import { defineComponent } from 'vue'

export default defineComponent({
  name: 'QuestionSection',
  data() {
    return {
      connectionStatus: 'connecting' as 'connecting' | 'connected' | 'error',
      mode: '' as '' | 'rejected' | 'idle' | 'counting' | 'interviewing',
      queueCount: 0,
      questionContent: '',
      waitingCount: 0,
      questionTitles: [],
      currentQuestion: -1,
      currentRate: null as number | null,
      currentComment: '' as string,
    }
  },
  components: {
    QuestionRejected,
    QuestionDisplay,
    QuestionIdle,
    QuestionCounting,
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

        if (data.type === 'reject') {
          this.mode = 'rejected'
        } else if (data.type === 'idle') {
          this.mode = 'idle'
        } else if (data.type === 'counting' && Array.isArray(data.questionTitles)) {
          this.mode = 'counting'
          this.questionTitles = data.questionTitles
          this.currentQuestion = -1
        } else if (
          data.type === 'interviewing' &&
          typeof data.currentQuestion === 'number' &&
          typeof data.content === 'string' &&
          Array.isArray(data.questionTitles) &&
          (data.rating === null || typeof data.rating === 'number') &&
          typeof data.comment === 'string'
        ) {
          this.mode = 'interviewing'
          this.currentQuestion = data.currentQuestion
          this.questionContent = data.content
          this.questionTitles = data.questionTitles
          this.currentRate = data.rating
          this.currentComment = data.comment
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
      this.mode = ''
    }
  },
})
