/**
 * Vocabulary Entry API Routes
 *
 * Handles CRUD operations for individual vocabulary entries:
 * - GET: Retrieve a single vocabulary entry
 * - PUT: Update custom fields of a vocabulary entry
 * - DELETE: Remove a vocabulary entry
 */

import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/db'
import { z } from 'zod'

// Validation schema for update requests
const updateVocabularySchema = z.object({
  customDefinition: z.string().max(2000).optional().nullable(),
  customPronunciation: z.string().max(200).optional().nullable(),
  customExamples: z.array(z.string().max(500)).max(10).optional().nullable(),
  customNotes: z.string().max(5000).optional().nullable(),
  customSynonyms: z.array(z.string().max(50)).max(20).optional().nullable(),
  customAntonyms: z.array(z.string().max(50)).max(20).optional().nullable(),
  customTags: z.array(z.string().max(30).regex(/^[a-z0-9-]+$/)).max(20).optional().nullable(),
})

type UpdateVocabularyRequest = z.infer<typeof updateVocabularySchema>

interface EditRecord {
  timestamp: string
  field: string
  action: 'added' | 'modified' | 'deleted'
}

/**
 * GET /api/vocabulary/[id]
 *
 * Retrieve a single vocabulary entry with all details
 */
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params

    const entry = await prisma.vocabularyEntry.findUnique({
      where: { id },
    })

    if (!entry) {
      return NextResponse.json(
        {
          error: 'Entry not found',
          code: 'ENTRY_NOT_FOUND',
          message: 'This vocabulary entry does not exist or has been deleted.',
          retryable: false,
        },
        { status: 404 }
      )
    }

    return NextResponse.json(entry)
  } catch (error) {
    console.error('Error fetching vocabulary entry:', error)
    return NextResponse.json(
      {
        error: 'Server error',
        code: 'INTERNAL_ERROR',
        message: 'Something went wrong. Please try again later.',
        retryable: true,
      },
      { status: 500 }
    )
  }
}

/**
 * PUT /api/vocabulary/[id]
 *
 * Update custom fields of a vocabulary entry
 * Tracks edit history for audit purposes
 */
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params
    const body = await request.json()

    // Validate request body
    const validationResult = updateVocabularySchema.safeParse(body)
    if (!validationResult.success) {
      const firstError = validationResult.error.errors[0]
      return NextResponse.json(
        {
          error: 'Validation failed',
          code: 'VALIDATION_ERROR',
          message: firstError.message,
          field: firstError.path.join('.'),
          retryable: false,
        },
        { status: 400 }
      )
    }

    const updateData = validationResult.data

    // Check if entry exists
    const existingEntry = await prisma.vocabularyEntry.findUnique({
      where: { id },
    })

    if (!existingEntry) {
      return NextResponse.json(
        {
          error: 'Entry not found',
          code: 'ENTRY_NOT_FOUND',
          message: 'This vocabulary entry does not exist or has been deleted.',
          retryable: false,
        },
        { status: 404 }
      )
    }

    // Build edit history records for changed fields
    const editHistory = (existingEntry.editHistory as unknown as EditRecord[]) || []
    const timestamp = new Date().toISOString()

    Object.keys(updateData).forEach((key) => {
      const field = key as keyof UpdateVocabularyRequest
      const oldValue = existingEntry[field]
      const newValue = updateData[field]

      // Only track if value actually changed
      if (JSON.stringify(oldValue) !== JSON.stringify(newValue)) {
        const action: 'added' | 'modified' | 'deleted' =
          newValue === null || newValue === undefined || (Array.isArray(newValue) && newValue.length === 0)
            ? 'deleted'
            : oldValue === null || oldValue === undefined
            ? 'added'
            : 'modified'

        editHistory.push({
          timestamp,
          field,
          action,
        })
      }
    })

    // Update the entry
    // Convert null to undefined for array fields (Prisma doesn't accept null for arrays)
    const prismaUpdateData: any = { ...updateData }
    if (prismaUpdateData.customExamples === null) prismaUpdateData.customExamples = []
    if (prismaUpdateData.customSynonyms === null) prismaUpdateData.customSynonyms = []
    if (prismaUpdateData.customAntonyms === null) prismaUpdateData.customAntonyms = []
    if (prismaUpdateData.customTags === null) prismaUpdateData.customTags = []

    const updatedEntry = await prisma.vocabularyEntry.update({
      where: { id },
      data: {
        ...prismaUpdateData,
        editHistory: editHistory as any,
        lastModified: new Date(),
      },
    })

    return NextResponse.json({
      id: updatedEntry.id,
      lastModified: updatedEntry.lastModified.toISOString(),
      message: 'Changes saved successfully!',
    })
  } catch (error) {
    console.error('Error updating vocabulary entry:', error)
    return NextResponse.json(
      {
        error: 'Server error',
        code: 'INTERNAL_ERROR',
        message: 'Something went wrong. Please try again later.',
        retryable: true,
      },
      { status: 500 }
    )
  }
}

/**
 * DELETE /api/vocabulary/[id]
 *
 * Remove a vocabulary entry
 * Idempotent - returns success even if entry doesn't exist
 */
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params

    // Try to delete the entry (idempotent - doesn't fail if not found)
    await prisma.vocabularyEntry.delete({
      where: { id },
    }).catch((error: any) => {
      // If error is "not found", that's OK (idempotent)
      if (!error.code || error.code !== 'P2025') {
        throw error
      }
    })

    return NextResponse.json({
      id,
      message: 'Word removed from your vocabulary.',
    })
  } catch (error) {
    console.error('Error deleting vocabulary entry:', error)
    return NextResponse.json(
      {
        error: 'Server error',
        code: 'INTERNAL_ERROR',
        message: 'Something went wrong. Please try again later.',
        retryable: true,
      },
      { status: 500 }
    )
  }
}
