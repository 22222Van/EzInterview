import QuestionDisplay from './QuestionViews/QuestionDisplay.vue'
import QuestionRejected from './QuestionViews/QuestionRejected.vue'
import QuestionIdle from './QuestionViews/QuestionIdle.vue'
import QuestionCounting from './QuestionViews/QuestionCounting.vue'
import {
  getSocket,
  getAvailableQuestions,
  getQuestionMains,
  setAvailableQuestions,
  setQuestionMains,
  setRealCurrentQuestion,
} from '@/socket'

import { defineComponent } from 'vue'

export default defineComponent({
  name: 'QuestionSection',
  data() {
    return {
      connectionStatus: 'connecting' as 'connecting' | 'connected' | 'error',
      mode: '' as '' | 'rejected' | 'idle' | 'counting' | 'interviewing',
      queueCount: 0,
      questionContent: '',
      questionKeywords: '',
      questionHint: '',
      waitingCount: 0,
      questionTitles: [],
      currentQuestion: -1,
      currentRate: null as number | null,
      currentComment: '' as string,
      availableQuestions: getAvailableQuestions(),
      questionMains: getQuestionMains(),
      showHint: false,
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
          this.questionTitles = []
        } else if (data.type === 'idle') {
          this.mode = 'idle'
          this.questionTitles = []
          setAvailableQuestions([])
          setQuestionMains([])
        } else if (
          data.type === 'counting' &&
          Array.isArray(data.questionTitles) &&
          Array.isArray(data.availableQuestions) &&
          Array.isArray(data.questionMains)
        ) {
          this.mode = 'counting'
          this.questionTitles = data.questionTitles
          this.currentQuestion = -1
          setAvailableQuestions(data.availableQuestions)
          setQuestionMains(data.questionMains)
          setRealCurrentQuestion(-1)
        } else if (
          data.type === 'interviewing' &&
          typeof data.currentQuestion === 'number' &&
          typeof data.questionMain === 'string' &&
          typeof data.questionKeywords === 'string' &&
          typeof data.questionHint === 'string' &&
          Array.isArray(data.questionTitles) &&
          (data.rating === null || typeof data.rating === 'number') &&
          typeof data.comment === 'string' &&
          Array.isArray(data.availableQuestions) &&
          Array.isArray(data.questionMains) &&
          typeof data.realCurrentQuestion === 'number' &&
          typeof data.hint === 'boolean'
        ) {
          this.mode = 'interviewing'
          this.currentQuestion = data.currentQuestion
          this.questionContent = data.questionMain
          this.questionKeywords = data.questionKeywords
          this.questionHint = data.questionHint
          this.questionTitles = data.questionTitles
          this.currentRate = data.rating
          this.currentComment = data.comment
          setAvailableQuestions(data.availableQuestions)
          setQuestionMains(data.questionMains)
          setRealCurrentQuestion(data.realCurrentQuestion)
          this.showHint = data.hint
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
