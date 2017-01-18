import matplotlib.pyplot as plt
import seaborn as sns
import pyfolio as pf
import utils

def show_result(daily_return, benchmark_daily_return, benchmark_title):
    """
    plot from metrics dictonary

    input
    ---------------------------
    daily_return: daily return of strategy
    benchmark_daily_return: daily return of benchmark
    benchmark_title: title of benchmark

    output
    ---------------------------
    return: None
    """
    daily_return.dropna(inplace=True)
    benchmark_daily_return.dropna(inplace=True)
    sharpe_ratio, max_drawdown, annual_return, total_return = utils.metrics(daily_return)
    bench_sharpe, bench_max_drawdown, bench_annual_return, bench_total_return = utils.metrics(benchmark_daily_return)
    metrics_dict = {"sharpe": sharpe_ratio, "max_drawdown": max_drawdown,
                    "annual_return": annual_return, "total_return": total_return,
                    "benchmark_sharpe": bench_sharpe, "benchmark_max_drawdown": bench_max_drawdown,
                    "benchmark_annual_return": bench_annual_return, "benchmark_total_return": bench_total_return}

    font_size = 15
    value_font_size = 12
    label_height, value_height = 0.8, 0.6
    label_height2, value_height2 = 0.35, 0.15
    red = "#aa4643"
    blue = "#4572a7"
    black = "#000000"

    fig_data = [
        (0.00, label_height, value_height, "Total Returns", "{0:.3%}".format(metrics_dict["total_return"]), red, black),
        (0.00, label_height2, value_height2, "Benchmark Total", "{0:.3%}".format(metrics_dict["benchmark_total_return"]), blue, black),

        (0.25, label_height, value_height, "Annual Returns", "{0:.3%}".format(metrics_dict["annual_return"]), red, black),
        (0.25, label_height2, value_height2, "Benchmark Annual", "{0:.3%}".format(metrics_dict["benchmark_annual_return"]), blue, black),

        (0.50, label_height, value_height, "Sharpe", "{0:.4}".format(metrics_dict["sharpe"]), red, black),
        (0.50, label_height2, value_height2, "Benchmark Sharpe", "{0:.4}".format(metrics_dict["benchmark_sharpe"]), blue, black),

        (0.75, label_height, value_height, "MaxDrawdown", "{0:.4}".format(metrics_dict["max_drawdown"]), red, black),
        (0.75, label_height2, value_height2, "Benchmark MaxDrawdown", "{0:.4}".format(metrics_dict["benchmark_max_drawdown"]), blue, black),
    ]

    f, (ax1, ax2, ax3) = plt.subplots(3, figsize=(12, 8))
    ax1.axis('off')
    for x, y1, y2, label, value, label_color, value_color in fig_data:
        ax1.text(x, y1, label, color=label_color, fontsize=font_size)
        ax1.text(x, y2, value, color=value_color, fontsize=value_font_size)
    ax2.set_title("Net value")
    ax2.set_xticklabels('')
    ax2.plot((1 + benchmark_daily_return).index, (1 + benchmark_daily_return).cumprod(), label=benchmark_title)
    ax2.plot((1 + daily_return).index, (1 + daily_return).cumprod(), label='Net value')
    ax2.legend()
    ax3 = pf.plot_drawdown_underwater(daily_return)
    plt.show()
