import { defineComponent } from 'vue'

interface Student {
  name: string
  id: string
}

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
    }
  },
})
