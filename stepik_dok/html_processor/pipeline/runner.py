import os
from html_processor.pipeline.steps import parser, analyzer, generator
from html_processor.utils.logger import log_info, log_error
from html_processor.pipeline.reporter import generate_summary_plot

def run_pipeline(config):
    input_dir = config['input_dir']
    output_dir = config['output_dir']
    overwrite = config['overwrite_output']
    options = config.get('analysis_options')
    generate_plot = config.get('generate_report_plot')

    os.makedirs(output_dir, exist_ok=True)

    success, errors, total_records = 0, 0, 0
    parsed_data_list = []

    log_info(f"Parsing HTML files from: {input_dir}")
    for filename in sorted(os.listdir(input_dir)):  # Sort files to ensure consistent order
        if filename.endswith('.html'):
            try:
                file_path = os.path.join(input_dir, filename)
                parsed_data = parser.parse_html_files(file_path)
                parsed_data_list.append((filename, parsed_data))
                record_count = len(parsed_data)
                log_info(f"Successfully parsed file: {filename} ({record_count} records)")
                success += 1
                total_records += record_count
            except Exception as e:
                log_error(f"Failed to parse file {filename}: {e}")
                errors += 1

    log_info("Analyzing extracted data...")
    for filename, parsed_data in parsed_data_list:
        analyzed_data = analyzer.analyze_data(parsed_data, options)
        log_info(f"Generating PDF report for: {filename}")
        generator.generate_pdf_reports(analyzed_data, output_dir, filename, overwrite)

    log_info("--------------------")
    log_info("Pipeline finished.")
    log_info(f"Successfully processed: {success} files ({total_records} total records).")
    if errors:
        log_error(f"Encountered errors: {errors} files.")

    if generate_plot:
        log_info("Generating summary plot...")
        stats = {
            'success': success,
            'error': errors,
            'total_records': total_records
        }
        output_path = os.path.join(output_dir, 'processing_summary.png')
        generate_summary_plot(stats, output_path)
        log_info("--------------------")
