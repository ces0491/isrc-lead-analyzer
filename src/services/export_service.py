"""
Export Service for Precise Digital Lead Generation Tool
Handles data export in various formats for CRM integration and reporting
Part of the Prism Analytics Engine
"""

import os
import io
import csv
import json
import xlsxwriter
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

# Optional imports for advanced features
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

class ExportService:
    """
    Service for exporting lead data in various formats
    Supports CSV, Excel, JSON, and PDF exports with Prism branding
    """
    
    def __init__(self):
        self.export_formats = ['csv', 'excel', 'json', 'pdf']
        self.default_fields = [
            'name', 'country', 'region', 'genre', 'total_score',
            'independence_score', 'opportunity_score', 'geographic_score',
            'lead_tier', 'monthly_listeners', 'outreach_status',
            'contact_email', 'website'
        ]
        
        # YouTube fields for enhanced exports
        self.youtube_fields = [
            'youtube_channel_id', 'youtube_channel_url', 'youtube_subscribers',
            'youtube_total_views', 'youtube_video_count', 'youtube_upload_frequency',
            'youtube_growth_potential', 'youtube_engagement_rate'
        ]
        
        # Prism branding configuration
        self.prism_branding = {
            'company_name': 'Precise Digital',
            'report_title': 'Prism Analytics Engine - Lead Generation Report',
            'tagline': 'Transforming Music Data into Actionable Insights',
            'primary_color': '#1A1A1A',
            'accent_color': '#E50914'
        }
    
    def export_leads(self, leads_data: List[Dict[str, Any]], 
                    export_format: str = 'csv',
                    include_youtube: bool = True,
                    custom_fields: Optional[List[str]] = None,
                    filters_applied: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main export function that handles all formats
        
        Args:
            leads_data: List of lead dictionaries
            export_format: Format to export (csv, excel, json, pdf)
            include_youtube: Whether to include YouTube metrics
            custom_fields: Custom field selection
            filters_applied: Information about applied filters
            
        Returns:
            Dictionary with export result and metadata
        """
        if not leads_data:
            return {
                'success': False,
                'error': 'No data to export',
                'export_info': {}
            }
        
        if export_format not in self.export_formats:
            return {
                'success': False,
                'error': f'Unsupported format: {export_format}',
                'supported_formats': self.export_formats
            }
        
        try:
            # Prepare data for export
            processed_data = self._prepare_export_data(
                leads_data, include_youtube, custom_fields
            )
            
            # Generate export based on format
            if export_format == 'csv':
                result = self._export_csv(processed_data, filters_applied)
            elif export_format == 'excel':
                result = self._export_excel(processed_data, filters_applied)
            elif export_format == 'json':
                result = self._export_json(processed_data, filters_applied)
            elif export_format == 'pdf':
                result = self._export_pdf(processed_data, filters_applied)
            
            # Add metadata
            result['export_info'] = {
                'format': export_format,
                'record_count': len(leads_data),
                'generated_at': datetime.utcnow().isoformat(),
                'include_youtube': include_youtube,
                'filters_applied': filters_applied or {},
                'prism_analytics': True
            }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Export failed: {str(e)}',
                'export_info': {}
            }
    
    def _prepare_export_data(self, leads_data: List[Dict[str, Any]],
                           include_youtube: bool = True,
                           custom_fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Prepare and normalize data for export"""
        
        # Determine fields to include
        fields = custom_fields or self.default_fields.copy()
        if include_youtube:
            fields.extend(self.youtube_fields)
        
        processed_data = []
        
        for lead in leads_data:
            row = {}
            
            # Basic fields
            row['name'] = lead.get('name', '')
            row['country'] = lead.get('country', '')
            row['region'] = lead.get('region', '')
            row['genre'] = lead.get('genre', '')
            
            # Scores
            row['total_score'] = lead.get('total_score', 0)
            row['independence_score'] = lead.get('independence_score', 0)
            row['opportunity_score'] = lead.get('opportunity_score', 0)
            row['geographic_score'] = lead.get('geographic_score', 0)
            row['lead_tier'] = lead.get('lead_tier', '')
            
            # Metrics
            row['monthly_listeners'] = lead.get('monthly_listeners', 0)
            
            # Contact info
            row['outreach_status'] = lead.get('outreach_status', '')
            row['contact_email'] = lead.get('contact_email', '')
            row['website'] = lead.get('website', '')
            
            # Social handles (convert dict to string)
            social_handles = lead.get('social_handles', {})
            if isinstance(social_handles, dict):
                social_str = ', '.join([f"{platform}: {handle}" for platform, handle in social_handles.items()])
                row['social_handles'] = social_str
            else:
                row['social_handles'] = str(social_handles) if social_handles else ''
            
            # YouTube metrics
            if include_youtube:
                youtube_summary = lead.get('youtube_summary', {})
                row['youtube_channel_id'] = youtube_summary.get('channel_id', '')
                row['youtube_channel_url'] = youtube_summary.get('channel_url', '')
                row['youtube_subscribers'] = youtube_summary.get('subscribers', 0)
                row['youtube_total_views'] = youtube_summary.get('total_views', 0)
                row['youtube_video_count'] = youtube_summary.get('video_count', 0)
                row['youtube_upload_frequency'] = youtube_summary.get('upload_frequency', '')
                row['youtube_growth_potential'] = youtube_summary.get('growth_potential', '')
                row['youtube_engagement_rate'] = youtube_summary.get('engagement_rate', 0.0)
                
                # YouTube opportunity indicators
                row['has_youtube_channel'] = 'Yes' if youtube_summary.get('has_channel') else 'No'
            
            # Timestamps
            row['created_at'] = lead.get('created_at', '')
            row['updated_at'] = lead.get('updated_at', '')
            
            # Additional calculated fields
            row['last_release_date'] = lead.get('last_release_date', '')
            
            # Priority classification
            row['priority'] = self._classify_priority(lead)
            
            # YouTube opportunity classification
            if include_youtube:
                row['youtube_opportunity'] = self._classify_youtube_opportunity(youtube_summary)
            
            # Filter fields based on selection
            if custom_fields:
                filtered_row = {field: row.get(field, '') for field in custom_fields}
                processed_data.append(filtered_row)
            else:
                processed_data.append(row)
        
        return processed_data
    
    def _export_csv(self, data: List[Dict[str, Any]], 
                   filters_applied: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Export data as CSV"""
        
        if not data:
            return {'success': False, 'error': 'No data to export'}
        
        output = io.StringIO()
        
        # Get field names from first record
        fieldnames = list(data[0].keys())
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        # Write header with Prism branding comment
        output.write(f"# {self.prism_branding['report_title']}\n")
        output.write(f"# Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
        output.write(f"# Records: {len(data)}\n")
        if filters_applied:
            output.write(f"# Filters: {', '.join([f'{k}={v}' for k, v in filters_applied.items() if v])}\n")
        output.write("#\n")
        
        # Write headers and data
        writer.writeheader()
        writer.writerows(data)
        
        csv_content = output.getvalue()
        output.close()
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'prism_leads_export_{timestamp}.csv'
        
        return {
            'success': True,
            'content': csv_content,
            'filename': filename,
            'content_type': 'text/csv'
        }
    
    def _export_excel(self, data: List[Dict[str, Any]], 
                     filters_applied: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Export data as Excel with formatting"""
        
        if not data:
            return {'success': False, 'error': 'No data to export'}
        
        # Create in-memory Excel file
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # Create worksheet
        worksheet = workbook.add_worksheet('Prism Leads Export')
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'font_color': 'white',
            'bg_color': '#1A1A1A',  # Prism black
            'border': 1
        })
        
        tier_a_format = workbook.add_format({'bg_color': '#C6EFCE'})  # Light green
        tier_b_format = workbook.add_format({'bg_color': '#FFEB9C'})  # Light yellow
        tier_c_format = workbook.add_format({'bg_color': '#FFC7CE'})  # Light red
        
        number_format = workbook.add_format({'num_format': '#,##0'})
        percent_format = workbook.add_format({'num_format': '0.00%'})
        
        # Write title and metadata
        title_format = workbook.add_format({'bold': True, 'font_size': 16})
        worksheet.write(0, 0, self.prism_branding['report_title'], title_format)
        worksheet.write(1, 0, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        worksheet.write(2, 0, f"Records: {len(data)}")
        
        if filters_applied:
            filters_str = ', '.join([f'{k}={v}' for k, v in filters_applied.items() if v])
            worksheet.write(3, 0, f"Filters Applied: {filters_str}")
        
        # Start data from row 5
        start_row = 5
        
        if not data:
            worksheet.write(start_row, 0, "No data to display")
            workbook.close()
            excel_content = output.getvalue()
            return {
                'success': True,
                'content': excel_content,
                'filename': f'prism_leads_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
                'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            }
        
        # Write headers
        headers = list(data[0].keys())
        for col, header in enumerate(headers):
            worksheet.write(start_row, col, header.replace('_', ' ').title(), header_format)
        
        # Write data with conditional formatting
        for row, record in enumerate(data, start=start_row + 1):
            for col, (key, value) in enumerate(record.items()):
                
                # Apply conditional formatting based on lead tier
                cell_format = None
                if key == 'lead_tier':
                    if value == 'A':
                        cell_format = tier_a_format
                    elif value == 'B':
                        cell_format = tier_b_format
                    elif value == 'C':
                        cell_format = tier_c_format
                
                # Apply number formatting
                elif key in ['monthly_listeners', 'youtube_subscribers', 'youtube_total_views', 'youtube_video_count']:
                    cell_format = number_format
                elif key in ['youtube_engagement_rate']:
                    value = value / 100 if isinstance(value, (int, float)) and value > 1 else value
                    cell_format = percent_format
                
                worksheet.write(row, col, value, cell_format)
        
        # Auto-adjust column widths
        for col, header in enumerate(headers):
            max_width = max(len(header), 10)
            if col < len(data):
                # Sample first few rows to estimate width
                sample_data = [str(data[i].get(header, '')) for i in range(min(5, len(data)))]
                if sample_data:
                    max_width = max(max_width, max(len(val) for val in sample_data))
            worksheet.set_column(col, col, min(max_width + 2, 50))
        
        # Add summary statistics worksheet
        if len(data) > 1:
            self._add_summary_worksheet(workbook, data)
        
        workbook.close()
        excel_content = output.getvalue()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'prism_leads_export_{timestamp}.xlsx'
        
        return {
            'success': True,
            'content': excel_content,
            'filename': filename,
            'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
    
    def _export_json(self, data: List[Dict[str, Any]], 
                    filters_applied: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Export data as JSON with metadata"""
        
        export_data = {
            'metadata': {
                'generated_by': self.prism_branding['company_name'],
                'report_title': self.prism_branding['report_title'],
                'generated_at': datetime.utcnow().isoformat(),
                'record_count': len(data),
                'filters_applied': filters_applied or {},
                'prism_analytics_version': '1.0.0'
            },
            'summary': self._generate_summary_stats(data) if data else {},
            'leads': data
        }
        
        json_content = json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'prism_leads_export_{timestamp}.json'
        
        return {
            'success': True,
            'content': json_content,
            'filename': filename,
            'content_type': 'application/json'
        }
    
    def _export_pdf(self, data: List[Dict[str, Any]], 
                   filters_applied: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Export data as PDF report"""
        
        if not HAS_REPORTLAB:
            return {
                'success': False,
                'error': 'PDF export requires reportlab library'
            }
        
        if not data:
            return {'success': False, 'error': 'No data to export'}
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title = Paragraph(self.prism_branding['report_title'], styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Metadata
        meta_text = f"""
        <b>Generated:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC<br/>
        <b>Total Records:</b> {len(data)}<br/>
        <b>Company:</b> {self.prism_branding['company_name']}<br/>
        """
        
        if filters_applied:
            filters_str = ', '.join([f'{k}={v}' for k, v in filters_applied.items() if v])
            meta_text += f"<b>Filters Applied:</b> {filters_str}<br/>"
        
        meta_para = Paragraph(meta_text, styles['Normal'])
        story.append(meta_para)
        story.append(Spacer(1, 20))
        
        # Summary statistics
        if len(data) > 1:
            summary_stats = self._generate_summary_stats(data)
            summary_title = Paragraph("<b>Summary Statistics</b>", styles['Heading2'])
            story.append(summary_title)
            
            summary_data = [
                ['Metric', 'Value'],
                ['Total Leads', len(data)],
                ['Average Score', f"{summary_stats.get('average_total_score', 0):.1f}"],
                ['Tier A Leads', summary_stats.get('tier_distribution', {}).get('A', 0)],
                ['Tier B Leads', summary_stats.get('tier_distribution', {}).get('B', 0)],
                ['Artists with YouTube', summary_stats.get('youtube_statistics', {}).get('artists_with_youtube', 0)]
            ]
            
            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 20))
        
        # Data table (limit to top records to avoid PDF being too large)
        max_records = min(50, len(data))
        if max_records < len(data):
            note = Paragraph(f"<i>Showing top {max_records} records out of {len(data)} total records</i>", styles['Normal'])
            story.append(note)
            story.append(Spacer(1, 12))
        
        # Select key fields for PDF table
        pdf_fields = ['name', 'country', 'lead_tier', 'total_score', 'monthly_listeners', 'outreach_status']
        if any('youtube_subscribers' in record for record in data):
            pdf_fields.append('youtube_subscribers')
        
        # Create table data
        table_data = [pdf_fields]  # Header row
        
        for i in range(max_records):
            record = data[i]
            row = [str(record.get(field, '')) for field in pdf_fields]
            table_data.append(row)
        
        # Create and style table
        data_table = Table(table_data)
        data_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        story.append(data_table)
        
        # Build PDF
        doc.build(story)
        pdf_content = buffer.getvalue()
        buffer.close()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'prism_leads_report_{timestamp}.pdf'
        
        return {
            'success': True,
            'content': pdf_content,
            'filename': filename,
            'content_type': 'application/pdf'
        }
    
    def _add_summary_worksheet(self, workbook, data: List[Dict[str, Any]]):
        """Add summary statistics worksheet to Excel export"""
        
        summary_sheet = workbook.add_worksheet('Summary Statistics')
        
        # Formats
        header_format = workbook.add_format({'bold': True, 'font_size': 14})
        subheader_format = workbook.add_format({'bold': True, 'bg_color': '#F2F2F2'})
        
        row = 0
        
        # Title
        summary_sheet.write(row, 0, 'Prism Analytics - Lead Summary', header_format)
        row += 2
        
        # Generate statistics
        stats = self._generate_summary_stats(data)
        
        # Basic statistics
        summary_sheet.write(row, 0, 'Basic Statistics', subheader_format)
        row += 1
        summary_sheet.write(row, 0, 'Total Leads')
        summary_sheet.write(row, 1, len(data))
        row += 1
        summary_sheet.write(row, 0, 'Average Total Score')
        summary_sheet.write(row, 1, f"{stats.get('average_total_score', 0):.1f}")
        row += 2
        
        # Tier distribution
        summary_sheet.write(row, 0, 'Lead Tier Distribution', subheader_format)
        row += 1
        tier_dist = stats.get('tier_distribution', {})
        for tier in ['A', 'B', 'C', 'D']:
            summary_sheet.write(row, 0, f'Tier {tier}')
            summary_sheet.write(row, 1, tier_dist.get(tier, 0))
            row += 1
        row += 1
        
        # Geographic distribution
        summary_sheet.write(row, 0, 'Geographic Distribution', subheader_format)
        row += 1
        geo_dist = stats.get('geographic_distribution', {})
        for region, count in geo_dist.items():
            summary_sheet.write(row, 0, region.replace('_', ' ').title())
            summary_sheet.write(row, 1, count)
            row += 1
        row += 1
        
        # YouTube statistics
        youtube_stats = stats.get('youtube_statistics', {})
        if youtube_stats:
            summary_sheet.write(row, 0, 'YouTube Statistics', subheader_format)
            row += 1
            summary_sheet.write(row, 0, 'Artists with YouTube Channels')
            summary_sheet.write(row, 1, youtube_stats.get('artists_with_youtube', 0))
            row += 1
            summary_sheet.write(row, 0, 'Total YouTube Subscribers')
            summary_sheet.write(row, 1, youtube_stats.get('total_subscribers', 0))
            row += 1
            summary_sheet.write(row, 0, 'Average Subscribers')
            summary_sheet.write(row, 1, f"{youtube_stats.get('average_subscribers', 0):.0f}")
        
        # Auto-adjust column widths
        summary_sheet.set_column(0, 0, 25)
        summary_sheet.set_column(1, 1, 15)
    
    def _generate_summary_stats(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics for the exported data"""
        
        if not data:
            return {}
        
        stats = {
            'total_records': len(data),
            'tier_distribution': {},
            'geographic_distribution': {},
            'outreach_distribution': {},
            'youtube_statistics': {}
        }
        
        # Calculate basic stats
        total_scores = [record.get('total_score', 0) for record in data if isinstance(record.get('total_score'), (int, float))]
        if total_scores:
            stats['average_total_score'] = sum(total_scores) / len(total_scores)
            stats['max_total_score'] = max(total_scores)
            stats['min_total_score'] = min(total_scores)
        
        # Tier distribution
        from collections import Counter
        tiers = [record.get('lead_tier', '') for record in data]
        stats['tier_distribution'] = dict(Counter(tiers))
        
        # Geographic distribution
        regions = [record.get('region', 'unknown') for record in data]
        stats['geographic_distribution'] = dict(Counter(regions))
        
        # Outreach status distribution
        statuses = [record.get('outreach_status', 'unknown') for record in data]
        stats['outreach_distribution'] = dict(Counter(statuses))
        
        # YouTube statistics
        youtube_channels = [record for record in data if record.get('has_youtube_channel') == 'Yes']
        stats['youtube_statistics'] = {
            'artists_with_youtube': len(youtube_channels),
            'youtube_coverage_percentage': (len(youtube_channels) / len(data)) * 100,
        }
        
        if youtube_channels:
            youtube_subs = [record.get('youtube_subscribers', 0) for record in youtube_channels if isinstance(record.get('youtube_subscribers'), (int, float))]
            if youtube_subs:
                stats['youtube_statistics'].update({
                    'total_subscribers': sum(youtube_subs),
                    'average_subscribers': sum(youtube_subs) / len(youtube_subs),
                    'max_subscribers': max(youtube_subs)
                })
        
        return stats
    
    def _classify_priority(self, lead: Dict[str, Any]) -> str:
        """Classify lead priority based on multiple factors"""
        
        total_score = lead.get('total_score', 0)
        tier = lead.get('lead_tier', 'D')
        outreach_status = lead.get('outreach_status', '')
        
        # High priority conditions
        if (tier == 'A' and outreach_status == 'not_contacted') or total_score >= 80:
            return 'High'
        
        # Medium priority conditions
        elif (tier in ['A', 'B'] and outreach_status in ['not_contacted', 'contacted']) or total_score >= 60:
            return 'Medium'
        
        # Low priority
        else:
            return 'Low'
    
    def _classify_youtube_opportunity(self, youtube_summary: Dict[str, Any]) -> str:
        """Classify YouTube opportunity level"""
        
        if not youtube_summary.get('has_channel'):
            return 'No Channel - High Opportunity'
        
        subscribers = youtube_summary.get('subscribers', 0)
        upload_frequency = youtube_summary.get('upload_frequency', '')
        growth_potential = youtube_summary.get('growth_potential', '')
        
        if growth_potential == 'high_potential':
            return 'High Growth Potential'
        elif subscribers < 1000 and upload_frequency in ['low', 'inactive']:
            return 'Underutilized Channel'
        elif subscribers > 10000 and upload_frequency == 'very_active':
            return 'Well Established'
        else:
            return 'Moderate Opportunity'

class BulkExportManager:
    """
    Manager for handling large bulk exports with progress tracking
    """
    
    def __init__(self):
        self.export_service = ExportService()
        self.chunk_size = 1000  # Process in chunks of 1000 records
    
    def export_large_dataset(self, query_params: Dict[str, Any], 
                           export_format: str = 'csv',
                           progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        Export large datasets with chunking and progress tracking
        """
        try:
            from config.database import DatabaseManager, Artist
            
            with DatabaseManager() as db:
                # Build query based on parameters
                query = db.session.query(Artist)
                
                # Apply filters (this would be expanded based on query_params)
                if query_params.get('tier'):
                    query = query.filter(Artist.lead_tier == query_params['tier'])
                
                if query_params.get('region'):
                    query = query.filter(Artist.region == query_params['region'])
                
                # Get total count
                total_count = query.count()
                
                if total_count == 0:
                    return {'success': False, 'error': 'No records found'}
                
                # Process in chunks
                all_data = []
                processed = 0
                
                for offset in range(0, total_count, self.chunk_size):
                    chunk = query.offset(offset).limit(self.chunk_size).all()
                    
                    # Convert to dict format
                    chunk_data = [artist.to_dict() for artist in chunk]
                    all_data.extend(chunk_data)
                    
                    processed += len(chunk_data)
                    
                    # Update progress
                    if progress_callback:
                        progress = (processed / total_count) * 100
                        progress_callback(processed, total_count, progress)
                
                # Perform export
                return self.export_service.export_leads(
                    all_data, 
                    export_format=export_format,
                    filters_applied=query_params
                )
        
        except Exception as e:
            return {'success': False, 'error': f'Bulk export failed: {str(e)}'}

# Utility functions for testing and validation
def test_export_service():
    """Test the export service with sample data"""
    
    export_service = ExportService()
    
    # Sample test data
    test_data = [
        {
            'name': 'Test Artist 1',
            'country': 'NZ',
            'region': 'new_zealand',
            'genre': 'indie rock',
            'total_score': 85.5,
            'independence_score': 40,
            'opportunity_score': 35,
            'geographic_score': 30,
            'lead_tier': 'A',
            'monthly_listeners': 15000,
            'outreach_status': 'not_contacted',
            'contact_email': 'contact@testartist1.com',
            'website': 'https://testartist1.com',
            'youtube_summary': {
                'has_channel': True,
                'channel_url': 'https://youtube.com/testartist1',
                'subscribers': 5000,
                'total_views': 500000,
                'video_count': 25,
                'upload_frequency': 'moderate',
                'growth_potential': 'high_potential',
                'engagement_rate': 3.2
            },
            'created_at': '2024-01-15T10:30:00Z',
            'updated_at': '2024-01-15T10:30:00Z'
        },
        {
            'name': 'Test Artist 2',
            'country': 'AU',
            'region': 'australia',
            'genre': 'electronic',
            'total_score': 72.0,
            'independence_score': 35,
            'opportunity_score': 30,
            'geographic_score': 25,
            'lead_tier': 'B',
            'monthly_listeners': 8000,
            'outreach_status': 'contacted',
            'contact_email': '',
            'website': '',
            'youtube_summary': {
                'has_channel': False,
                'channel_url': '',
                'subscribers': 0,
                'total_views': 0,
                'video_count': 0,
                'upload_frequency': '',
                'growth_potential': '',
                'engagement_rate': 0.0
            },
            'created_at': '2024-01-16T14:20:00Z',
            'updated_at': '2024-01-16T14:20:00Z'
        }
    ]
    
    # Test all export formats
    formats = ['csv', 'json', 'excel']
    
    for format_type in formats:
        print(f"\n🧪 Testing {format_type.upper()} export...")
        
        result = export_service.export_leads(
            test_data,
            export_format=format_type,
            include_youtube=True,
            filters_applied={'test': True}
        )
        
        if result['success']:
            print(f"  ✅ {format_type.upper()} export successful")
            print(f"  📁 Filename: {result['filename']}")
            print(f"  📊 Records: {result['export_info']['record_count']}")
            if format_type == 'csv':
                print(f"  📝 Content preview: {result['content'][:200]}...")
        else:
            print(f"  ❌ {format_type.upper()} export failed: {result['error']}")

def create_sample_export():
    """Create a sample export file for demonstration"""
    
    export_service = ExportService()
    
    # Generate sample data
    sample_leads = []
    regions = ['new_zealand', 'australia', 'pacific_islands', 'other']
    tiers = ['A', 'B', 'C', 'D']
    genres = ['indie rock', 'electronic', 'folk', 'hip-hop', 'pop']
    
    import random
    
    for i in range(20):
        lead = {
            'name': f'Sample Artist {i+1}',
            'country': random.choice(['NZ', 'AU', 'US', 'GB', 'FJ']),
            'region': random.choice(regions),
            'genre': random.choice(genres),
            'total_score': round(random.uniform(30, 95), 1),
            'independence_score': random.randint(0, 40),
            'opportunity_score': random.randint(0, 40),
            'geographic_score': random.randint(0, 30),
            'lead_tier': random.choice(tiers),
            'monthly_listeners': random.randint(1000, 100000),
            'outreach_status': random.choice(['not_contacted', 'contacted', 'responded']),
            'contact_email': f'contact@sampleartist{i+1}.com' if random.random() > 0.3 else '',
            'website': f'https://sampleartist{i+1}.com' if random.random() > 0.4 else '',
            'youtube_summary': {
                'has_channel': random.random() > 0.3,
                'subscribers': random.randint(0, 50000) if random.random() > 0.3 else 0,
                'upload_frequency': random.choice(['very_active', 'active', 'moderate', 'low', 'inactive']),
                'growth_potential': random.choice(['high_potential', 'moderate_potential', 'low_potential'])
            }
        }
        sample_leads.append(lead)
    
    # Export as Excel
    result = export_service.export_leads(
        sample_leads,
        export_format='excel',
        include_youtube=True
    )
    
    if result['success']:
        # Save to file
        with open(result['filename'], 'wb') as f:
            f.write(result['content'])
        print(f"✅ Sample export created: {result['filename']}")
    else:
        print(f"❌ Failed to create sample export: {result['error']}")

if __name__ == "__main__":
    test_export_service()
    print("\n" + "="*60)
    create_sample_export()