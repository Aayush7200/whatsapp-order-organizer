# WhatsApp Order Organizer

**Problem:** Small shops take orders over WhatsApp. At the end of the day the owner re-reads
hundreds of messages to work out what to pack/buy and who ordered what: slow and error-prone.

**Solution:** Export the chat -> run one command -> get a clean `orders.csv` (opens in Excel/Sheets)
and a `summary.txt` with per-day totals and a per-customer breakdown.

## Usage
```
python orders.py chat.txt --out output/
python test_orders.py
```
Zero dependencies (Python 3.8+). Works with Android and iOS WhatsApp exports.

## Key design decisions
- **Rule-based parsing, not an LLM:** orders follow a tiny grammar (qty + unit + item), so regex is
  free, instant, offline, and deterministic. An LLM could hallucinate quantities.
- **Ignore chatter safely:** messages with no quantity ("thanks!") are skipped rather than guessed.
- **Cancellations:** "cancel" removes that customer's latest order of the day.
- **Local-language synonyms** (`tamatar -> tomato`) live in one dict the shop can extend.

## Real-world result (fill in honestly after testing with a real shop)
- Tested with: ___ (shop/club name), ___ days of chat, ___ orders
- Parsing accuracy: ___% (checked by hand against the owner's own tally)
- Time saved: from ___ min/day to ___ min/day

## Known limitations / next steps
- Unit conversion (500 g vs 0.5 kg), Hindi/Hinglish script items, price totals, Telegram bot so
  customers get an auto-confirmation.
