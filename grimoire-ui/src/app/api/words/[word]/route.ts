/**
 * Word Lookup API Route
 *
 * Proxies word lookup requests to the FastAPI backend.
 * Implements caching, error handling, and response validation.
 */

import { NextRequest, NextResponse } from 'next/server'
import { enhancedWordDataSchema } from '@/types/contracts'
import { createErrorResponse, httpStatusToErrorCode } from '@/lib/errors'

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000'
const CACHE_DURATION = 300 // 5 minutes in seconds

// Map CEFR levels to difficulty levels
function mapDifficultyLevel(cefrLevel?: string): 'beginner' | 'intermediate' | 'advanced' | 'expert' | undefined {
  if (!cefrLevel) return undefined
  const cefr = cefrLevel.toUpperCase()
  if (cefr === 'A1' || cefr === 'A2') return 'beginner'
  if (cefr === 'B1' || cefr === 'B2') return 'intermediate'
  if (cefr === 'C1') return 'advanced'
  if (cefr === 'C2') return 'expert'
  return undefined
}

/**
 * GET /api/words/[word]
 *
 * Look up a word from the FastAPI backend.
 */
export async function GET(
  request: NextRequest,
  { params }: { params: { word: string } }
) {
  try {
    const word = params.word

    // Validate word parameter
    if (!word || word.trim().length === 0) {
      return NextResponse.json(
        createErrorResponse('INVALID_INPUT', 'Word parameter is required'),
        { status: 400 }
      )
    }

    // Call FastAPI backend
    const response = await fetch(`${FASTAPI_URL}/api/v1/words/${encodeURIComponent(word)}`, {
      headers: {
        'Accept': 'application/json',
      },
    })

    // Handle error responses
    if (!response.ok) {
      const errorCode = httpStatusToErrorCode(response.status)
      let errorMessage: string

      try {
        const errorData = await response.json()
        errorMessage = errorData.detail || errorData.message || response.statusText
      } catch {
        errorMessage = response.statusText
      }

      return NextResponse.json(
        createErrorResponse(errorCode, errorMessage),
        { status: response.status }
      )
    }

    // Parse and transform response from backend format to UI format
    const backendData = await response.json()

    // Transform backend schema to match UI expectations
    const transformedData = {
      word: backendData.word_text,
      phonetics: backendData.phonetic ? [{
        text: backendData.phonetic.ipa_transcription,
        audio: backendData.phonetic.audio_url || undefined,
      }] : [],
      meanings: backendData.definitions?.map((def: any) => ({
        partOfSpeech: def.part_of_speech,
        definitions: [{
          definition: def.definition_text,
          example: def.examples?.[0]?.example_text,
          synonyms: [],
          antonyms: [],
        }],
        synonyms: backendData.related_words
          ?.filter((rw: any) => rw.relationship_type === 'synonym')
          .map((rw: any) => rw.word) || [],
        antonyms: backendData.related_words
          ?.filter((rw: any) => rw.relationship_type === 'antonym')
          .map((rw: any) => rw.word) || [],
      })) || [],
      sourceUrls: [],
      difficulty: mapDifficultyLevel(backendData.learning_metadata?.difficulty_level),
      frequency: backendData.learning_metadata?.frequency_rank || undefined,
      styleTags: backendData.learning_metadata?.style_tags || [],
      relatedWords: backendData.related_words?.map((rw: any) => rw.word) || [],
      etymology: undefined,
    }

    // Validate transformed data
    const validationResult = enhancedWordDataSchema.safeParse(transformedData)

    if (!validationResult.success) {
      return NextResponse.json(
        createErrorResponse(
          'VALIDATION_ERROR',
          'Invalid response format from word lookup service',
          validationResult.error.errors
        ),
        { status: 500 }
      )
    }

    // Return success response with caching headers
    return NextResponse.json(validationResult.data, {
      headers: {
        'Cache-Control': `public, s-maxage=${CACHE_DURATION}, stale-while-revalidate`,
      },
    })
  } catch (error) {
    console.error('Word lookup error:', error)

    // Handle network errors
    if (error instanceof TypeError) {
      return NextResponse.json(
        createErrorResponse('NETWORK_ERROR', 'Failed to connect to word lookup service'),
        { status: 503 }
      )
    }

    // Handle unknown errors
    return NextResponse.json(
      createErrorResponse(
        'INTERNAL_ERROR',
        error instanceof Error ? error.message : 'An unexpected error occurred'
      ),
      { status: 500 }
    )
  }
}

// Enable caching for this route
export const revalidate = CACHE_DURATION
