import QuestionDisplay from './QuestionViews/QuestionDisplay.vue'
import QuestionWaiting from './QuestionViews/QuestionWaiting.vue'

import { defineComponent } from 'vue'

export default defineComponent({
  name: 'QuestionSection',
  data() {
    return {
      connectionStatus: 'connecting' as 'connecting' | 'connected' | 'error',
      mode: '' as '' | 'waiting' | 'question',
      questionContent: '',
      waitingCount: 0,
      steps: ['Step 1', 'Step 2', 'Step 3'],
      currentStep: 1, // 控制当前高亮的步骤（从0开始）
    }
  },
  components: {
    QuestionWaiting,
    QuestionDisplay,
  },
  mounted() {
    const host = window.location.hostname
    const port = '9008'
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
          this.waitingCount = data.count
        } else if (data.type === 'question' && typeof data.content === 'string') {
          this.mode = 'question'
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
      this.mode = ''
    }
  },
})
