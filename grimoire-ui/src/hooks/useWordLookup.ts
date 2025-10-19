'use client'

/**
 * useWordLookup Hook
 *
 * Manages word lookup state, loading, errors, and API calls.
 * Provides a clean interface for word search functionality.
 * Includes automatic retry logic for transient errors.
 */

import { useState, useCallback } from 'react'
import type { EnhancedWordData, ErrorResponse } from '@/types/contracts'
import { enhancedWordDataSchema } from '@/types/contracts'
import { apiClient, isErrorResponse } from '@/lib/api-client'
import { isRetryable } from '@/lib/errors'

export interface UseWordLookupReturn {
  wordData: EnhancedWordData | null
  isLoading: boolean
  error: string | null
  errorCode: string | null
  retryable: boolean
  lookupWord: (word: string) => Promise<void>
  retry: () => Promise<void>
  clearError: () => void
  clearData: () => void
}

const MAX_RETRIES = 3
const RETRY_DELAYS = [1000, 2000, 4000] // Exponential backoff: 1s, 2s, 4s

export function useWordLookup(): UseWordLookupReturn {
  const [wordData, setWordData] = useState<EnhancedWordData | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [errorCode, setErrorCode] = useState<string | null>(null)
  const [retryable, setRetryable] = useState(false)
  const [lastWord, setLastWord] = useState<string>('')

  const attemptLookup = async (word: string, retryCount = 0): Promise<boolean> => {
    try {
      // Call API
      const result = await apiClient.get(
        `/api/words/${encodeURIComponent(word)}`,
        enhancedWordDataSchema
      )

      // Check for errors
      if (isErrorResponse(result)) {
        // Check if error is retryable
        const canRetry = isRetryable(result.code)

        // If retryable and we haven't exhausted retries, try again
        if (canRetry && retryCount < MAX_RETRIES) {
          const delay = RETRY_DELAYS[retryCount]
          console.log(`Retrying word lookup in ${delay}ms (attempt ${retryCount + 1}/${MAX_RETRIES})`)
          await new Promise(resolve => setTimeout(resolve, delay))
          return attemptLookup(word, retryCount + 1)
        }

        // Set error state
        setError(result.message)
        setErrorCode(result.code)
        setRetryable(result.retryable)
        setWordData(null)
        return false
      }

      // Success
      setWordData(result)
      setError(null)
      setErrorCode(null)
      setRetryable(false)
      return true
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred'

      // Network errors are retryable
      const isNetworkError = err instanceof TypeError
      if (isNetworkError && retryCount < MAX_RETRIES) {
        const delay = RETRY_DELAYS[retryCount]
        console.log(`Retrying word lookup after network error in ${delay}ms (attempt ${retryCount + 1}/${MAX_RETRIES})`)
        await new Promise(resolve => setTimeout(resolve, delay))
        return attemptLookup(word, retryCount + 1)
      }

      setError(errorMessage)
      setErrorCode('NETWORK_ERROR')
      setRetryable(isNetworkError)
      setWordData(null)
      return false
    }
  }

  const lookupWord = useCallback(async (word: string) => {
    // Reset state
    setError(null)
    setErrorCode(null)
    setRetryable(false)
    setIsLoading(true)
    setLastWord(word)

    await attemptLookup(word, 0)
    setIsLoading(false)
  }, [])

  const retry = useCallback(async () => {
    if (lastWord) {
      await lookupWord(lastWord)
    }
  }, [lastWord, lookupWord])

  const clearError = useCallback(() => {
    setError(null)
    setErrorCode(null)
    setRetryable(false)
  }, [])

  const clearData = useCallback(() => {
    setWordData(null)
    setError(null)
    setErrorCode(null)
    setRetryable(false)
  }, [])

  return {
    wordData,
    isLoading,
    error,
    errorCode,
    retryable,
    lookupWord,
    retry,
    clearError,
    clearData,
  }
}
