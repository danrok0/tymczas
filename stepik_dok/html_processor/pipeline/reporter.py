import matplotlib.pyplot as plt
from html_processor.utils.logger import log_info, log_error

def generate_summary_plot(stats, output_path):
    """Generates a summary plot showing processing statistics.
    
    Args:
        stats: Dictionary containing statistics (success, error, total_records)
        output_path: Path where to save the plot image
    """
    try:
        log_info("Generating summary plot...")
        labels = ['Success', 'Error', 'Total Records']
        values = [stats['success'], stats['error'], stats['total_records']]

        plt.figure(figsize=(8, 6))
        plt.bar(labels, values, color=['green', 'red', 'blue'])
        plt.title('HTML to PDF Processing Summary')
        plt.savefig(output_path)
        plt.close()
        log_info(f"Summary plot saved to: {output_path}")
    except Exception as e:
        log_error(f"Failed to generate summary plot: {e}")