# Streamlit manual UI checks

Start from the repository root:

```powershell
.venv\Scripts\python.exe -m streamlit run app.py --server.headless true
```

Open the printed local URL. All operations below use saved capture bytes only.
The initial dashboard opens the real `normal_traffic.pcap` built-in demo.

| Check | Action and expected result |
| --- | --- |
| 1. Launch | The dark dashboard renders without a traceback. Header, sidebar, traffic lights, cards, and charts are visible. |
| 2. Normal PCAP | Open `normal_traffic.pcap` from either demo control. Real summary values appear and no anomaly alerts are reported. |
| 3. Normal PCAPNG | Open `normal_traffic.pcapng`. No alerts appear. Format must show the backend-detected format, even if the filename extension differs from the file contents. |
| 4. Port scan | Open `port_scan.pcap`. Security Alerts includes `POSSIBLE_PORT_SCAN`, HIGH severity, and the real unique-port evidence. |
| 5. High rate | Open `high_rate.pcap`. Security Alerts includes `HIGH_PACKET_RATE`, MEDIUM severity, packet count, and packets per second. |
| 6. Combined patterns | Open `suspicious_traffic.pcap`. Both alert types appear; the Alerts KPI equals the returned alert-list length. |
| 7. Corruption | Upload invalid bytes in a `.pcap`, then a `.pcapng`. Analyze. A concise error appears; the previous valid capture is clearly identified and remains available. |
| 8. Extension | Try selecting `.txt`. The native uploader rejects it. Renaming malformed bytes to `.pcap` must still fail backend validation. |
| 9. Metadata | Verify filename, detected format, packet count, UTC start/end, duration, truncation state against the service result. |
| 10. Protocol chart | Five protocol categories use distinct restrained colors; percentage/count labels and donut hover values match backend values. Empty captures show an explanatory empty state. |
| 11. Timeline | Hover bars to inspect real packets and bytes. Axis timestamps are UTC. Empty captures show an explanatory empty state. |
| 12. Rankings | Source/destination ranks, packet counts, proportional bars, and captured bytes agree with backend rankings. Overview shows the first five; Statistics shows all returned ranks. Null IPs are absent. |
| 13. Sizes | Minimum, maximum, mean, median, and p95 match backend values with human-readable units. |
| 14. Packet table | Preview shows at most 500 real packet rows. Timestamp/ports/protocol/transport/length/flags/DNS columns render. Scroll within the table. |
| 15. Navigation | All five sidebar views change visible content. Settings shows real default thresholds as read-only information. |
| 16. Persistence | Switch views, change packet filters, and open/close popovers. Capture results persist without repeating service analysis. Open another demo; results update. |
| 17. Warnings | With a capture above the packet limit, verify `Truncated: Yes` and every parser warning appears in Capture Information. |
| 18. Desktop sizing | Inspect at 1440×900, 1920×1080, and 1080-wide desktop sizes. Main content uses available width; charts/cards remain legible without page-wide horizontal overflow. |
| 19. Empty / oversized | Upload an empty capture and a file larger than 25 MiB. Both are rejected politely. A structurally valid zero-packet capture returns complete empty sections. |
| 20. Filters | On Packet Analysis, select protocols and enter source/destination substrings. Matching rows update; an unmatched query shows zero rows. Clearing filters restores the appropriate results. |

Security wording must describe possible/potential heuristic patterns. The no-alert
state must include that it does not guarantee absence of malicious activity.
Never use live packet transmission, capture, or scanning to perform these checks.
