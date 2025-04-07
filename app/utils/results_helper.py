def analyze_scan_results(results, filename=None):
    context = {
        "results": results,
        "filename": filename,
        "show_results_content": False,
        "show_failed_content": False,
        "card_border": "border-secondary",
        "card_header_bg": "bg-secondary text-white",
        "attributes": {},
        "stats": {},
        "is_malicious": False,
        "is_suspicious": False
    }

    if results:
        attributes = results["data"]["attributes"]
        stats = attributes["stats"]
        is_malicious = stats["malicious"] > 0
        is_suspicious = stats["suspicious"] > 0

        context.update({
            "show_results_content": True,
            "attributes": attributes,
            "stats": stats,
            "is_malicious": is_malicious,
            "is_suspicious": is_suspicious,
            "card_border": (
                "border-danger" if is_malicious else
                "border-warning" if is_suspicious else
                "border-success"
            ),
            "card_header_bg": (
                "bg-danger text-white" if is_malicious else
                "bg-warning text-dark" if is_suspicious else
                "bg-success text-white"
            )
        })

    elif filename:
        context.update({
            "show_failed_content": True,
            "card_border": "border-warning",
            "card_header_bg": "bg-warning text-dark"
        })

    return context
