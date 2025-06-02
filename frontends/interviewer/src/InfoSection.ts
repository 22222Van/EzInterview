import { defineComponent, ref, watch } from 'vue'
import type { PropType } from 'vue'

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
  props: {
    availableQuestions: {
      type: Array as PropType<number[]>,
      default: () => [],
    },
    questionMains: {
      type: Array as PropType<string[]>,
      default: () => [],
    },
  },
  setup(props) {
    const selectedIndexes = ref([...props.availableQuestions])

    watch(
      () => props.availableQuestions,
      (newVal) => {
        selectedIndexes.value = [...newVal]
      },
    )

    const sendChange = () => {
      alert(selectedIndexes.value)
    }

    return {
      selectedIndexes,
      sendChange,
    }
  },
})
