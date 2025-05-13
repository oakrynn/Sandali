import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

def generate_bar_chart(stats, title):
    """
    Generate a visually appealing bar chart for spending by category.
    """
    # Extract categories and amounts
    categories, amounts = zip(*stats) if stats else ([], [])
    if not categories:
        categories = ["No Data"]
        amounts = [0]

    # Set Seaborn style for a modern look
    sns.set_style("whitegrid")
    plt.style.use("seaborn-v0_8")

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))

    # Use the Spectral color palette for vibrant, cohesive colors
    colors = sns.color_palette("Spectral", len(categories))

    # Plot bars with rounded edges and slight transparency
    bars = ax.bar(categories, amounts, color=colors, edgecolor="black", alpha=0.85)

    # Add value labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.05 * max(amounts, default=1),
            f"${height:.2f}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold"
        )

    # Customize title and labels
    ax.set_title(title, fontsize=16, fontweight="bold", pad=20)
    ax.set_xlabel("Categories", fontsize=12)
    ax.set_ylabel("Amount ($)", fontsize=12)

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha="right", fontsize=10)

    # Add a subtle grid for better readability
    ax.yaxis.grid(True, linestyle="--", alpha=0.7)
    ax.xaxis.grid(False)

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    # Save the chart
    output_path = f"charts/bar_{title.replace(' ', '_')}.png"
    os.makedirs("charts", exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    return output_path

def generate_pie_chart(stats, title):
    """
    Generate a 2D pie chart with:
    - Title in the top-left corner, smaller font.
    - Category labels in a legend in the top-left corner.
    - Smaller percentage labels outside the circumference with curved connecting lines.
    """
    # Extract categories and amounts
    categories, amounts = zip(*stats) if stats else ([], [])
    if not categories:
        categories = ["No Data"]
        amounts = [0]

    # Set Seaborn style for consistency
    sns.set_style("whitegrid")
    plt.style.use("seaborn-v0_8")

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 8))

    # Use the Spectral color palette for vibrant colors
    colors = sns.color_palette("Spectral", len(categories))

    # Plot 2D pie chart without labels or percentages directly on the chart
    wedges, _ = ax.pie(
        amounts,
        colors=colors,
        startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 1}
    )

    # Calculate percentages
    total = sum(amounts)
    percentages = [(amount / total * 100) if total > 0 else 0 for amount in amounts]

    # Add category legend in the top-left corner
    legend_labels = [f"{cat} (${amt:.2f})" for cat, amt in zip(categories, amounts)]
    ax.legend(
        wedges,
        legend_labels,
        title="Categories",
        loc="upper left",
        bbox_to_anchor=(0, 0.9),  # Adjusted to make room for title
        fontsize=9,
        title_fontsize=10,
        frameon=True,
        edgecolor="black"
    )

    # Add smaller percentage labels outside the circumference with curved lines
    for i, (wedge, percentage) in enumerate(zip(wedges, percentages)):
        # Get the angle and radius for the wedge
        ang = (wedge.theta2 + wedge.theta1) / 2
        x = np.cos(np.radians(ang))
        y = np.sin(np.radians(ang))

        # Position the percentage label further outside the pie
        label_x = 1.3 * x
        label_y = 1.3 * y

        # Connection line from pie edge to label with curved style
        ax.annotate(
            f"{percentage:.1f}%",
            xy=(x, y),  # Edge of the pie
            xytext=(label_x, label_y),  # Label position
            textcoords="data",
            fontsize=7,  # Smaller font size
            fontweight="bold",
            color="black",
            ha="center",
            va="center",
            arrowprops=dict(
                arrowstyle="-",
                color="black",
                linewidth=0.5,
                connectionstyle="arc3,rad=0.2"  # Curved lines
            )
        )

    # Add title in the top-left corner, smaller font
    ax.text(
        0, 1,  # Top-left corner
        title,
        fontsize=12,  # Smaller than previous (was 16)
        fontweight="bold",
        transform=ax.transAxes,  # Use axes coordinates
        ha="left",
        va="top"
    )

    # Equal aspect ratio for a circular pie chart
    ax.axis("equal")

    # Save the chart
    output_path = f"charts/pie_{title.replace(' ', '_')}.png"
    os.makedirs("charts", exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    return output_path