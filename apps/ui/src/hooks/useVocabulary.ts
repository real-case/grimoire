'use client'

/**
 * useVocabulary Hook
 *
 * Manages vocabulary list state and CRUD operations.
 */

import { useState, useCallback, useEffect } from 'react'
import type {
  VocabularyListItem,
  Pagination,
  VocabularyListResponse,
  CreateVocabularyRequest,
} from '@/types/contracts'
import { apiClient, isErrorResponse } from '@/lib/api-client'
import { z } from 'zod'

const vocabularyListResponseSchema = z.object({
  entries: z.array(z.any()),
  pagination: z.object({
    page: z.number(),
    limit: z.number(),
    total: z.number(),
    totalPages: z.number(),
    hasNext: z.boolean(),
    hasPrevious: z.boolean(),
  }),
})

export interface UseVocabularyReturn {
  entries: VocabularyListItem[]
  pagination: Pagination | null
  isLoading: boolean
  error: string | null
  fetchVocabulary: (params?: {
    page?: number
    limit?: number
    sortBy?: 'savedAt' | 'lastModified' | 'word'
    order?: 'asc' | 'desc'
    search?: string
    tags?: string[]
  }) => Promise<void>
  saveWord: (data: CreateVocabularyRequest) => Promise<boolean>
  clearError: () => void
}

export function useVocabulary(): UseVocabularyReturn {
  const [entries, setEntries] = useState<VocabularyListItem[]>([])
  const [pagination, setPagination] = useState<Pagination | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchVocabulary = useCallback(async (params: {
    page?: number
    limit?: number
    sortBy?: 'savedAt' | 'lastModified' | 'word'
    order?: 'asc' | 'desc'
    search?: string
    tags?: string[]
  } = {}) => {
    setError(null)
    setIsLoading(true)

    try {
      // Build query string
      const queryParams = new URLSearchParams()
      if (params.page !== undefined) queryParams.set('page', params.page.toString())
      if (params.limit !== undefined) queryParams.set('limit', params.limit.toString())
      if (params.sortBy) queryParams.set('sortBy', params.sortBy)
      if (params.order) queryParams.set('order', params.order)
      if (params.search) queryParams.set('search', params.search)
      if (params.tags && params.tags.length > 0) queryParams.set('tags', params.tags.join(','))

      const result = await apiClient.get(
        `/api/vocabulary?${queryParams.toString()}`,
        vocabularyListResponseSchema
      )

      if (isErrorResponse(result)) {
        setError(result.message)
        return
      }

      setEntries(result.entries as VocabularyListItem[])
      setPagination(result.pagination)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch vocabulary')
    } finally {
      setIsLoading(false)
    }
  }, [])

  const saveWord = useCallback(async (data: CreateVocabularyRequest): Promise<boolean> => {
    setError(null)

    try {
      const result = await apiClient.post(
        '/api/vocabulary',
        z.object({
          id: z.string(),
          word: z.string(),
          savedAt: z.string(),
          lastModified: z.string(),
          message: z.string(),
        }),
        data
      )

      if (isErrorResponse(result)) {
        setError(result.message)
        return false
      }

      // Refresh the list after saving
      await fetchVocabulary()
      return true
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save word')
      return false
    }
  }, [fetchVocabulary])

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  return {
    entries,
    pagination,
    isLoading,
    error,
    fetchVocabulary,
    saveWord,
    clearError,
  }
}
