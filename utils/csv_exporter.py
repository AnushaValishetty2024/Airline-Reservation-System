"""CSV Export Utility for Analytics Reports."""
import csv
import io
from datetime import datetime
from flask import Response
from services.business_analytics_service import BusinessAnalyticsService


def generate_csv_response(data, filename_prefix, column_names):
    """Generate CSV response for download."""
    if not data or not column_names:
        return None
    
    # Create string buffer for CSV
    output = io.StringIO()
    
    # Write CSV data
    writer = csv.DictWriter(output, fieldnames=column_names)
    writer.writeheader()
    
    for row in data:
        # Convert any non-string values to strings
        row_dict = {}
        for col in column_names:
            value = row.get(col, '')
            if value is None:
                value = ''
            elif isinstance(value, (int, float)):
                value = str(value)
            else:
                value = str(value)
            row_dict[col] = value
        writer.writerow(row_dict)
    
    # Create response
    output.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{filename_prefix}_{timestamp}.csv"
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename={filename}',
            'Content-Type': 'text/csv'
        }
    )


def export_revenue_report(service=None, start_date=None, end_date=None):
    """Export revenue report as CSV."""
    if service is None:
        service = BusinessAnalyticsService()
    data, column_names = service.export_analytics_data('revenue', start_date, end_date)
    if not column_names:
        column_names = ['date', 'bookings', 'revenue', 'avg_transaction', 'unique_customers']
    return generate_csv_response(data, 'revenue_report', column_names)


def export_booking_report(service=None, start_date=None, end_date=None):
    """Export booking report as CSV."""
    if service is None:
        service = BusinessAnalyticsService()
    data, column_names = service.export_analytics_data('bookings', start_date, end_date)
    if not column_names:
        column_names = ['booking_reference', 'booked_at', 'status_name', 'customer', 
                       'flight_number', 'airline_name', 'total_amount']
    return generate_csv_response(data, 'booking_report', column_names)


def export_customer_report(service=None):
    """Export customer report as CSV."""
    if service is None:
        service = BusinessAnalyticsService()
    data, column_names = service.export_analytics_data('customers')
    if not column_names:
        column_names = ['id', 'full_name', 'email', 'mobile_number', 'registration_date',
                       'total_bookings', 'total_spent']
    return generate_csv_response(data, 'customer_report', column_names)


def export_flight_report(service=None, start_date=None, end_date=None):
    """Export flight report as CSV."""
    if service is None:
        service = BusinessAnalyticsService()
    data, column_names = service.export_analytics_data('flights', start_date, end_date)
    if not column_names:
        column_names = ['flight_number', 'airline_name', 'departure_datetime', 'arrival_datetime',
                       'status', 'total_bookings', 'revenue']
    return generate_csv_response(data, 'flight_report', column_names)


def export_route_report(service=None):
    """Export route report as CSV."""
    if service is None:
        service = BusinessAnalyticsService()
    data, column_names = service.export_analytics_data('routes')
    if not column_names:
        column_names = ['route', 'airline_name', 'flight_count', 'booking_count', 'total_revenue']
    return generate_csv_response(data, 'route_report', column_names)


def export_payment_report(service=None, start_date=None, end_date=None):
    """Export payment report as CSV."""
    if service is None:
        service = BusinessAnalyticsService()
    data, column_names = service.export_analytics_data('payments', start_date, end_date)
    if not column_names:
        column_names = ['payment_reference', 'paid_at', 'amount', 'payment_method', 
                       'payment_status', 'customer']
    return generate_csv_response(data, 'payment_report', column_names)


def export_occupancy_report(service=None):
    """Export occupancy report as CSV."""
    if service is None:
        service = BusinessAnalyticsService()
    data, column_names = service.export_analytics_data('occupancy')
    if not column_names:
        column_names = ['airline_name', 'total_flights', 'total_capacity', 'seats_sold', 'occupancy_rate']
    return generate_csv_response(data, 'occupancy_report', column_names)


def export_cancellation_report(service=None, start_date=None, end_date=None):
    """Export cancellation report as CSV."""
    if service is None:
        service = BusinessAnalyticsService()
    data, column_names = service.export_analytics_data('cancellations', start_date, end_date)
    if not column_names:
        column_names = ['booking_reference', 'booked_at', 'customer', 'flight_number', 
                       'airline_name', 'total_amount']
    return generate_csv_response(data, 'cancellation_report', column_names)


def export_report(service, report_type):
    """Export analytics report based on report type."""
    data, column_names = service.export_analytics_data(report_type)
    if not column_names:
        return None
    return generate_csv_response(data, f'{report_type}_report', column_names)


def export_power_bi_dataset(dataset_name):
    """Export Power BI dataset as CSV."""
    service = BusinessAnalyticsService()
    try:
        datasets = service.prepare_power_bi_datasets()
        data = datasets.get(dataset_name)
        
        if not data:
            return None
        
        # Get column names from first row
        column_names = list(data[0].keys()) if data else []
        
        return generate_csv_response(data, f'powerbi_{dataset_name}', column_names)
    finally:
        service.close()


def export_all_power_bi_datasets():
    """Export all Power BI datasets as a zip file."""
    import zipfile
    import io
    
    service = BusinessAnalyticsService()
    zip_buffer = None
    try:
        datasets = service.prepare_power_bi_datasets()
    
        # Create zip file in memory
        zip_buffer = io.BytesIO()
    
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for dataset_name, data in datasets.items():
                if data:
                    # Create CSV content
                    output = io.StringIO()
                    column_names = list(data[0].keys())
                    writer = csv.DictWriter(output, fieldnames=column_names)
                    writer.writeheader()
                    
                    for row in data:
                        row_dict = {}
                        for col in column_names:
                            value = row.get(col, '')
                            if value is None:
                                value = ''
                            elif isinstance(value, (int, float)):
                                value = str(value)
                            else:
                                value = str(value)
                            row_dict[col] = value
                        writer.writerow(row_dict)
                    
                    # Add to zip
                    zip_file.writestr(f'{dataset_name}.csv', output.getvalue())
    finally:
        service.close()
    
    if zip_buffer:
        zip_buffer.seek(0)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return Response(
            zip_buffer.getvalue(),
            mimetype='application/zip',
            headers={
                'Content-Disposition': f'attachment; filename=power_bi_datasets_{timestamp}.zip',
                'Content-Type': 'application/zip'
            }
        )
    return None


class CSVExporter:
    """CSV Export Utility."""

    @staticmethod
    def export_report(service, report_type):
        if report_type == "revenue":
            return export_revenue_report(service)
        elif report_type == "bookings":
            return export_booking_report(service)
        elif report_type == "customers":
            return export_customer_report(service)
        elif report_type == "flights":
            return export_flight_report(service)
        elif report_type == "routes":
            return export_route_report(service)
        elif report_type == "payments":
            return export_payment_report(service)
        elif report_type == "occupancy":
            return export_occupancy_report(service)
        elif report_type == "cancellations":
            return export_cancellation_report(service)
        return None

    @staticmethod
    def export_power_bi_dataset(dataset_name):
        try:
            return export_power_bi_dataset(dataset_name)
        except Exception:
            return None

    @staticmethod
    def export_all_power_bi_datasets():
        try:
            return export_all_power_bi_datasets()
        except Exception:
            return None
