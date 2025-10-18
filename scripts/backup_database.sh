#!/bin/bash

###############################################################################
# Database Backup Script for Grimoire
#
# This script:
# 1. Creates a compressed PostgreSQL database backup using pg_dump
# 2. Uploads the backup to cloud storage (AWS S3, Google Cloud Storage, or local)
# 3. Cleans up old backups based on retention policy
# 4. Sends notifications on success/failure
#
# Usage:
#   ./scripts/backup_database.sh [--local] [--cloud <provider>]
#   ./scripts/backup_database.sh --local
#   ./scripts/backup_database.sh --cloud s3
#
# Requirements:
#   - pg_dump (PostgreSQL client tools)
#   - aws CLI (for S3 uploads)
#   - gsutil (for Google Cloud Storage uploads)
#   - DATABASE_URL environment variable
###############################################################################

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKUP_DIR="${BACKUP_DIR:-$PROJECT_ROOT/backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="grimoire_backup_${TIMESTAMP}.sql.gz"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_FILE"
RETENTION_DAYS="${RETENTION_DAYS:-7}"  # Keep backups for 7 days by default

# Cloud storage configuration
CLOUD_PROVIDER="${CLOUD_PROVIDER:-none}"  # s3, gcs, or none
S3_BUCKET="${S3_BUCKET:-}"
GCS_BUCKET="${GCS_BUCKET:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --local)
            CLOUD_PROVIDER="none"
            shift
            ;;
        --cloud)
            CLOUD_PROVIDER="$2"
            shift 2
            ;;
        --retention-days)
            RETENTION_DAYS="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--local] [--cloud <provider>] [--retention-days <days>]"
            exit 1
            ;;
    esac
done

# Function to log messages
log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Function to check if required command exists
check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 is not installed. Please install it first."
        exit 1
    fi
}

# Function to parse DATABASE_URL
parse_database_url() {
    # Load .env file if it exists
    if [ -f "$PROJECT_ROOT/.env" ]; then
        log_info "Loading environment variables from .env"
        export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
    fi

    # Check if DATABASE_URL is set
    if [ -z "$DATABASE_URL" ]; then
        log_error "DATABASE_URL environment variable is not set"
        exit 1
    fi

    # Parse DATABASE_URL (format: postgresql://user:pass@host:port/dbname)
    # Remove protocol prefix
    DB_URL_NO_PROTO="${DATABASE_URL#postgresql://}"
    DB_URL_NO_PROTO="${DB_URL_NO_PROTO#postgresql+asyncpg://}"

    # Extract credentials and connection info
    DB_USER=$(echo "$DB_URL_NO_PROTO" | cut -d':' -f1)
    DB_PASS=$(echo "$DB_URL_NO_PROTO" | cut -d'@' -f1 | cut -d':' -f2)
    DB_HOST=$(echo "$DB_URL_NO_PROTO" | cut -d'@' -f2 | cut -d':' -f1)
    DB_PORT=$(echo "$DB_URL_NO_PROTO" | cut -d'@' -f2 | cut -d':' -f2 | cut -d'/' -f1)
    DB_NAME=$(echo "$DB_URL_NO_PROTO" | cut -d'/' -f2 | cut -d'?' -f1)

    export PGPASSWORD="$DB_PASS"

    log_info "Database connection details:"
    log_info "  Host: $DB_HOST"
    log_info "  Port: $DB_PORT"
    log_info "  Database: $DB_NAME"
    log_info "  User: $DB_USER"
}

# Function to create backup directory
setup_backup_directory() {
    if [ ! -d "$BACKUP_DIR" ]; then
        log_info "Creating backup directory: $BACKUP_DIR"
        mkdir -p "$BACKUP_DIR"
    fi
}

# Function to create database backup
create_backup() {
    log_info "Starting database backup..."
    log_info "Backup file: $BACKUP_PATH"

    # Run pg_dump with compression
    if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        --format=plain --no-owner --no-acl | gzip > "$BACKUP_PATH"; then

        BACKUP_SIZE=$(du -h "$BACKUP_PATH" | cut -f1)
        log_info "Backup created successfully: $BACKUP_FILE ($BACKUP_SIZE)"
        return 0
    else
        log_error "Failed to create database backup"
        return 1
    fi
}

# Function to upload to AWS S3
upload_to_s3() {
    if [ -z "$S3_BUCKET" ]; then
        log_error "S3_BUCKET environment variable is not set"
        return 1
    fi

    check_command "aws"

    log_info "Uploading backup to S3: s3://$S3_BUCKET/$BACKUP_FILE"

    if aws s3 cp "$BACKUP_PATH" "s3://$S3_BUCKET/backups/$BACKUP_FILE"; then
        log_info "Backup uploaded to S3 successfully"
        return 0
    else
        log_error "Failed to upload backup to S3"
        return 1
    fi
}

# Function to upload to Google Cloud Storage
upload_to_gcs() {
    if [ -z "$GCS_BUCKET" ]; then
        log_error "GCS_BUCKET environment variable is not set"
        return 1
    fi

    check_command "gsutil"

    log_info "Uploading backup to GCS: gs://$GCS_BUCKET/$BACKUP_FILE"

    if gsutil cp "$BACKUP_PATH" "gs://$GCS_BUCKET/backups/$BACKUP_FILE"; then
        log_info "Backup uploaded to GCS successfully"
        return 0
    else
        log_error "Failed to upload backup to GCS"
        return 1
    fi
}

# Function to clean up old backups
cleanup_old_backups() {
    log_info "Cleaning up backups older than $RETENTION_DAYS days..."

    # Find and delete old local backups
    DELETED_COUNT=$(find "$BACKUP_DIR" -name "grimoire_backup_*.sql.gz" \
        -type f -mtime +$RETENTION_DAYS -delete -print | wc -l)

    if [ "$DELETED_COUNT" -gt 0 ]; then
        log_info "Deleted $DELETED_COUNT old backup(s)"
    else
        log_info "No old backups to delete"
    fi
}

# Function to verify backup integrity
verify_backup() {
    log_info "Verifying backup integrity..."

    if gzip -t "$BACKUP_PATH" 2>/dev/null; then
        log_info "Backup file integrity verified"
        return 0
    else
        log_error "Backup file is corrupted!"
        return 1
    fi
}

# Main execution
main() {
    log_info "========================================="
    log_info "Grimoire Database Backup Script"
    log_info "========================================="

    # Check required commands
    check_command "pg_dump"
    check_command "gzip"

    # Parse database connection details
    parse_database_url

    # Setup backup directory
    setup_backup_directory

    # Create backup
    if ! create_backup; then
        log_error "Backup failed!"
        exit 1
    fi

    # Verify backup
    if ! verify_backup; then
        log_error "Backup verification failed!"
        exit 1
    fi

    # Upload to cloud storage if configured
    case "$CLOUD_PROVIDER" in
        s3)
            upload_to_s3
            ;;
        gcs)
            upload_to_gcs
            ;;
        none)
            log_info "Local backup only (no cloud upload)"
            ;;
        *)
            log_warning "Unknown cloud provider: $CLOUD_PROVIDER"
            ;;
    esac

    # Cleanup old backups
    cleanup_old_backups

    log_info "========================================="
    log_info "Backup completed successfully!"
    log_info "Backup location: $BACKUP_PATH"
    log_info "========================================="
}

# Run main function
main
