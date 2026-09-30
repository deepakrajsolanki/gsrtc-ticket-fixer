# GSRTC Ticket PDF

Native Android utility for printing the ORIGINAL GSRTC ticket without reconstructing its HTML.

## Intended workflow

Chrome -> open GSRTC ticket -> Share -> GSRTC Ticket PDF -> wait -> PDF button -> Android Print -> Save as PDF.

## Important design rule

The app does NOT parse passenger/fare/logo data and does NOT recreate the ticket.

It loads the original GSRTC HTML in Android WebView and relies on wide-viewport/overview rendering plus Android's print engine to fit the complete rendered ticket to the PDF page.

This preserves the original logo, tables, typography, images and layout.

## Build

Open this folder in Android Studio and build/install the app.

If Android Studio asks for a Gradle wrapper, let it generate/sync the wrapper, or use a locally installed Gradle 8.9+.
