/**
 * API Contract Types - Grimoire UI
 *
 * This file contains Zod schemas and TypeScript types for API contracts.
 * These serve as the single source of truth for request/response validation.
 *
 * Usage:
 * 1. Import schemas for runtime validation
 * 2. Use z.infer<typeof schema> to derive TypeScript types
 * 3. Validate API responses: wordDataSchema.parse(apiResponse)
 */

import { z } from 'zod';

// =============================================================================
// Word Data (from FastAPI backend)
// =============================================================================

export const licenseSchema = z.object({
  name: z.string(),
  url: z.string().url(),
});

export const phoneticSchema = z.object({
  text: z.string().optional(),
  audio: z.string().url().optional(),
  sourceUrl: z.string().url().optional(),
  license: licenseSchema.optional(),
});

export const definitionSchema = z.object({
  definition: z.string(),
  example: z.string().optional(),
  synonyms: z.array(z.string()).optional(),
  antonyms: z.array(z.string()).optional(),
});

export const meaningSchema = z.object({
  partOfSpeech: z.string(),
  definitions: z.array(definitionSchema),
  synonyms: z.array(z.string()).optional(),
  antonyms: z.array(z.string()).optional(),
});

export const wordDataSchema = z.object({
  word: z.string(),
  phonetics: z.array(phoneticSchema),
  meanings: z.array(meaningSchema),
  license: licenseSchema.optional(),
  sourceUrls: z.array(z.string().url()).optional(),
});

export const enhancedWordDataSchema = wordDataSchema.extend({
  difficulty: z.enum(['beginner', 'intermediate', 'advanced', 'expert']).optional(),
  frequency: z.number().optional(),
  styleTags: z.array(z.string()).optional(),
  relatedWords: z.array(z.string()).optional(),
  etymology: z.string().optional(),
});

// TypeScript types derived from schemas
export type License = z.infer<typeof licenseSchema>;
export type Phonetic = z.infer<typeof phoneticSchema>;
export type Definition = z.infer<typeof definitionSchema>;
export type Meaning = z.infer<typeof meaningSchema>;
export type WordData = z.infer<typeof wordDataSchema>;
export type EnhancedWordData = z.infer<typeof enhancedWordDataSchema>;

// =============================================================================
// Vocabulary Entry
// =============================================================================

export const editRecordSchema = z.object({
  timestamp: z.string().datetime(),
  field: z.string(),
  action: z.enum(['added', 'modified', 'deleted']),
});

export const vocabularyEntrySchema = z.object({
  id: z.string().uuid(),
  word: z.string(),
  savedAt: z.string().datetime(),
  lastModified: z.string().datetime(),
  userId: z.string().nullable(),

  // Original API data
  originalData: enhancedWordDataSchema,

  // Custom fields
  customDefinition: z.string().max(2000).nullable(),
  customPronunciation: z.string().max(200).nullable(),
  customExamples: z.array(z.string().max(500)).max(10).nullable(),
  customNotes: z.string().max(5000).nullable(),
  customSynonyms: z.array(z.string().max(50)).max(20).nullable(),
  customAntonyms: z.array(z.string().max(50)).max(20).nullable(),
  customTags: z.array(z.string().max(30).regex(/^[a-z0-9-]+$/)).max(20).nullable(),

  // Edit history
  editHistory: z.array(editRecordSchema),
});

export type EditRecord = z.infer<typeof editRecordSchema>;
export type VocabularyEntry = z.infer<typeof vocabularyEntrySchema>;

// =============================================================================
// Vocabulary List Item (preview for list view)
// =============================================================================

export const vocabularyListItemSchema = z.object({
  id: z.string().uuid(),
  word: z.string(),
  savedAt: z.string().datetime(),
  lastModified: z.string().datetime(),
  hasCustomEdits: z.boolean(),
  preview: z.string().max(200),
  tags: z.array(z.string()),
});

export type VocabularyListItem = z.infer<typeof vocabularyListItemSchema>;

// =============================================================================
// API Request/Response Types
// =============================================================================

// Word Lookup
export type WordLookupResponse = EnhancedWordData;

// List Vocabulary
export const vocabularyListRequestSchema = z.object({
  page: z.number().int().min(0).default(0),
  limit: z.number().int().min(1).max(100).default(20),
  sortBy: z.enum(['savedAt', 'lastModified', 'word']).default('lastModified'),
  order: z.enum(['asc', 'desc']).default('desc'),
  search: z.string().optional(),
  tags: z.string().optional(), // Comma-separated
});

export const paginationSchema = z.object({
  page: z.number(),
  limit: z.number(),
  total: z.number(),
  totalPages: z.number(),
  hasNext: z.boolean(),
  hasPrevious: z.boolean(),
});

export const vocabularyListResponseSchema = z.object({
  entries: z.array(vocabularyListItemSchema),
  pagination: paginationSchema,
});

export type VocabularyListRequest = z.infer<typeof vocabularyListRequestSchema>;
export type Pagination = z.infer<typeof paginationSchema>;
export type VocabularyListResponse = z.infer<typeof vocabularyListResponseSchema>;

// Create Vocabulary
export const createVocabularyRequestSchema = z.object({
  word: z.string().min(1).max(100).regex(/^[a-zA-Z'-]+$/, 'Invalid word format'),
  originalData: enhancedWordDataSchema,
  customDefinition: z.string().max(2000).optional(),
  customPronunciation: z.string().max(200).optional(),
  customExamples: z.array(z.string().max(500)).max(10).optional(),
  customNotes: z.string().max(5000).optional(),
  customSynonyms: z.array(z.string().max(50)).max(20).optional(),
  customAntonyms: z.array(z.string().max(50)).max(20).optional(),
  customTags: z.array(z.string().max(30).regex(/^[a-z0-9-]+$/)).max(20).optional(),
});

export type CreateVocabularyRequest = z.infer<typeof createVocabularyRequestSchema>;

// Update Vocabulary
export const updateVocabularyRequestSchema = z.object({
  customDefinition: z.string().max(2000).optional(),
  customPronunciation: z.string().max(200).optional(),
  customExamples: z.array(z.string().max(500)).max(10).optional(),
  customNotes: z.string().max(5000).optional(),
  customSynonyms: z.array(z.string().max(50)).max(20).optional(),
  customAntonyms: z.array(z.string().max(50)).max(20).optional(),
  customTags: z.array(z.string().max(30).regex(/^[a-z0-9-]+$/)).max(20).optional(),
});

export type UpdateVocabularyRequest = z.infer<typeof updateVocabularyRequestSchema>;

// Mutation Response
export const vocabularyMutationResponseSchema = z.object({
  id: z.string().uuid(),
  word: z.string().optional(),
  savedAt: z.string().datetime().optional(),
  lastModified: z.string().datetime(),
  message: z.string(),
});

export type VocabularyMutationResponse = z.infer<typeof vocabularyMutationResponseSchema>;

// =============================================================================
// Error Response
// =============================================================================

export const errorResponseSchema = z.object({
  error: z.string(),
  code: z.string(),
  message: z.string(),
  field: z.string().optional(),
  retryable: z.boolean(),
  details: z.unknown().optional(),
});

export type ErrorResponse = z.infer<typeof errorResponseSchema>;

// Error codes enum
export const ErrorCode = {
  WORD_NOT_FOUND: 'WORD_NOT_FOUND',
  ENTRY_NOT_FOUND: 'ENTRY_NOT_FOUND',
  DUPLICATE_WORD: 'DUPLICATE_WORD',
  INVALID_INPUT: 'INVALID_INPUT',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  IMMUTABLE_FIELD: 'IMMUTABLE_FIELD',
  API_UNAVAILABLE: 'API_UNAVAILABLE',
  TIMEOUT: 'TIMEOUT',
  INTERNAL_ERROR: 'INTERNAL_ERROR',
  NETWORK_ERROR: 'NETWORK_ERROR',
} as const;

export type ErrorCodeType = typeof ErrorCode[keyof typeof ErrorCode];

// =============================================================================
// UI State Types (not part of API contract, but useful for implementation)
// =============================================================================

/**
 * EditableWord - UI state for editing a word
 * Combines API data with edit state tracking
 */
export interface EditableWord {
  // Metadata
  id?: string;
  word: string;
  savedAt?: Date;
  lastModified?: Date;

  // Original API data (immutable reference)
  originalData: EnhancedWordData;

  // Current display values (may be original or edited)
  displayDefinition: string;
  displayPronunciation?: string;
  displayExamples: string[];
  displayNotes?: string;
  displaySynonyms: string[];
  displayAntonyms: string[];
  displayTags: string[];

  // Edit tracking
  editedFields: Set<string>;
  isDirty: boolean;

  // UI state
  isLoading?: boolean;
  error?: string;
}

/**
 * Helper function to create EditableWord from API response
 */
export function createEditableWord(
  originalData: EnhancedWordData,
  saved?: VocabularyEntry
): EditableWord {
  return {
    id: saved?.id,
    word: originalData.word,
    savedAt: saved?.savedAt ? new Date(saved.savedAt) : undefined,
    lastModified: saved?.lastModified ? new Date(saved.lastModified) : undefined,

    originalData,

    // Display values prioritize custom over original
    displayDefinition: saved?.customDefinition ??
      originalData.meanings[0]?.definitions[0]?.definition ?? '',
    displayPronunciation: saved?.customPronunciation ??
      originalData.phonetics[0]?.text,
    displayExamples: saved?.customExamples ??
      originalData.meanings.flatMap(m =>
        m.definitions.map(d => d.example).filter(Boolean)
      ) as string[],
    displayNotes: saved?.customNotes ?? undefined,
    displaySynonyms: saved?.customSynonyms ??
      originalData.meanings.flatMap(m => m.synonyms ?? []),
    displayAntonyms: saved?.customAntonyms ??
      originalData.meanings.flatMap(m => m.antonyms ?? []),
    displayTags: saved?.customTags ?? [],

    editedFields: new Set(
      saved ? Object.keys(saved).filter(k => k.startsWith('custom') && saved[k as keyof VocabularyEntry] != null) : []
    ),
    isDirty: false,
  };
}

// =============================================================================
// Validation Helpers
// =============================================================================

/**
 * Validate and parse API response with proper error handling
 */
export function parseWordData(data: unknown): EnhancedWordData | ErrorResponse {
  try {
    return enhancedWordDataSchema.parse(data);
  } catch (error) {
    if (error instanceof z.ZodError) {
      return {
        error: 'Invalid response format',
        code: ErrorCode.VALIDATION_ERROR,
        message: 'The server returned an unexpected response format.',
        retryable: false,
        details: error.errors,
      };
    }
    throw error;
  }
}

/**
 * Validate vocabulary entry data
 */
export function validateVocabularyEntry(data: unknown): CreateVocabularyRequest | ErrorResponse {
  try {
    return createVocabularyRequestSchema.parse(data);
  } catch (error) {
    if (error instanceof z.ZodError) {
      const firstError = error.errors[0];
      return {
        error: 'Validation failed',
        code: ErrorCode.VALIDATION_ERROR,
        message: firstError.message,
        field: firstError.path.join('.'),
        retryable: false,
        details: error.errors,
      };
    }
    throw error;
  }
}
