import { defineStore } from 'pinia'

export const useStrategyStore = defineStore('strategy', {
  state: () => ({
    strategies: [],
    activeStrategy: null
  }),

  actions: {
    setStrategies(strategies) {
      this.strategies = strategies
    },

    addStrategy(strategy) {
      this.strategies.push(strategy)
    },

    updateStrategy(strategy) {
      const index = this.strategies.findIndex(s => s.id === strategy.id)
      if (index !== -1) {
        this.strategies[index] = strategy
      }
    },

    removeStrategy(strategyId) {
      this.strategies = this.strategies.filter(s => s.id !== strategyId)
    },

    setActiveStrategy(strategy) {
      this.activeStrategy = strategy
    }
  }
})

