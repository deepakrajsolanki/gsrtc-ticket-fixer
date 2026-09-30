package in.solaank.gsrtcticketpdf;

import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.print.PrintAttributes;
import android.print.PrintDocumentAdapter;
import android.print.PrintManager;
import android.view.View;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {

    private ScrollView panelHome;
    private FrameLayout panelWebView;
    private WebView webView;
    private ProgressBar progress;
    private Button btnPrint;
    private Button btnBack;
    private TextView txtHeaderTitle;
    private EditText editUrl;
    private Button btnPaste;
    private Button btnLoadTicket;
    private Button btnOpenGSRTC;

    private boolean isViewingTicket = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        initViews();
        setupWebView();
        setupListeners();

        // Handle incoming intent (e.g. Chrome Share sheet)
        handleIncomingIntent(getIntent());
    }

    private void initViews() {
        panelHome = findViewById(R.id.panelHome);
        panelWebView = findViewById(R.id.panelWebView);
        webView = findViewById(R.id.webView);
        progress = findViewById(R.id.progress);
        btnPrint = findViewById(R.id.btnPrint);
        btnBack = findViewById(R.id.btnBack);
        txtHeaderTitle = findViewById(R.id.txtHeaderTitle);
        editUrl = findViewById(R.id.editUrl);
        btnPaste = findViewById(R.id.btnPaste);
        btnLoadTicket = findViewById(R.id.btnLoadTicket);
        btnOpenGSRTC = findViewById(R.id.btnOpenGSRTC);
    }

    private void setupListeners() {
        btnPaste.setOnClickListener(v -> pasteFromClipboard());
        btnLoadTicket.setOnClickListener(v -> {
            String url = editUrl.getText().toString().trim();
            if (url.isEmpty()) {
                Toast.makeText(this, "Please paste or enter a ticket URL", Toast.LENGTH_SHORT).show();
                return;
            }
            loadTicketUrl(url);
        });

        btnOpenGSRTC.setOnClickListener(v -> {
            loadWebsiteUrl("https://www.gsrtc.in/");
        });

        btnBack.setOnClickListener(v -> handleBackNavigation());
        btnPrint.setOnClickListener(v -> printTicket());
    }

    private void pasteFromClipboard() {
        ClipboardManager clipboard = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
        if (clipboard != null && clipboard.hasPrimaryClip()) {
            ClipData clipData = clipboard.getPrimaryClip();
            if (clipData != null && clipData.getItemCount() > 0) {
                CharSequence text = clipData.getItemAt(0).getText();
                if (text != null) {
                    editUrl.setText(text.toString().trim());
                    Toast.makeText(this, "Pasted from clipboard", Toast.LENGTH_SHORT).show();
                    return;
                }
            }
        }
        Toast.makeText(this, "Clipboard is empty", Toast.LENGTH_SHORT).show();
    }

    private void setupWebView() {
        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setLoadsImagesAutomatically(true);
        s.setUseWideViewPort(true);
        s.setLoadWithOverviewMode(true);
        s.setBuiltInZoomControls(true);
        s.setDisplayZoomControls(false);
        s.setSupportZoom(true);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(true);

        webView.setBackgroundColor(Color.WHITE);

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageStarted(WebView view, String url, Bitmap favicon) {
                progress.setVisibility(View.VISIBLE);
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                progress.setVisibility(View.GONE);

                // Inject responsive CSS & DOM correction on ticket pages
                if (url != null && (url.contains("viewTicket") || url.contains("ticket") || isViewingTicket)) {
                    injectTicketFixScript(view);
                    btnPrint.setVisibility(View.VISIBLE);
                    Toast.makeText(MainActivity.this, "Ticket loaded & fixed! Tap 'Save PDF'.", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri uri = request.getUrl();
                String host = uri.getHost();
                if (host != null && host.contains("gsrtc.in")) {
                    return false;
                }
                // Open external links in default external browser
                Intent intent = new Intent(Intent.ACTION_VIEW, uri);
                startActivity(intent);
                return true;
            }
        });
    }

    private void injectTicketFixScript(WebView view) {
        String js = "javascript:(function() {" +
                "  var meta = document.querySelector('meta[name=\"viewport\"]');" +
                "  if (!meta) {" +
                "    meta = document.createElement('meta');" +
                "    meta.name = 'viewport';" +
                "    meta.content = 'width=device-width, initial-scale=1.0, maximum-scale=2.0';" +
                "    document.getElementsByTagName('head')[0].appendChild(meta);" +
                "  }" +
                "  var content = document.getElementById('content');" +
                "  if (content) {" +
                "    content.style.width = '100%';" +
                "    content.style.maxWidth = 'none';" +
                "    content.style.overflow = 'visible';" +
                "    content.style.boxSizing = 'border-box';" +
                "    content.style.padding = '8px';" +
                "  }" +
                "  document.body.style.width = '100%';" +
                "  document.body.style.margin = '0';" +
                "  document.body.style.padding = '0';" +
                "  document.body.style.overflow = 'visible';" +
                "  document.documentElement.style.overflow = 'visible';" +
                "  document.documentElement.style.width = '100%';" +
                "  var all = document.querySelectorAll('[style]');" +
                "  for (var i = 0; i < all.length; i++) {" +
                "    var el = all[i];" +
                "    if (['TABLE','TD','TR','TH'].indexOf(el.tagName) === -1) {" +
                "      var st = el.getAttribute('style') || '';" +
                "      if (st.match(/width\\s*:\\s*\\d+px/i)) {" +
                "        el.setAttribute('style', st.replace(/width\\s*:\\s*\\d+px/gi, 'width:100%').replace(/overflow\\s*:\\s*hidden/gi, 'overflow:visible'));" +
                "      }" +
                "    }" +
                "  }" +
                "  var rows = document.querySelectorAll('tr');" +
                "  for (var j = 0; j < rows.length; j++) {" +
                "    var row = rows[j];" +
                "    var txt = row.innerText || '';" +
                "    var cells = row.querySelectorAll('td');" +
                "    if (txt.indexOf('Boarding From') !== -1 && txt.indexOf('Arrival') !== -1 && cells.length === 2) {" +
                "      cells[0].style.width = '50%';" +
                "      cells[1].style.width = '50%';" +
                "    }" +
                "  }" +
                "})()";
        view.loadUrl(js);
    }

    private void handleIncomingIntent(Intent intent) {
        String url = null;
        if (Intent.ACTION_SEND.equals(intent.getAction())) {
            CharSequence shared = intent.getCharSequenceExtra(Intent.EXTRA_TEXT);
            if (shared != null) url = shared.toString().trim();
        } else if (Intent.ACTION_VIEW.equals(intent.getAction())) {
            Uri data = intent.getData();
            if (data != null) url = data.toString();
        }

        if (url != null && !url.isEmpty() && url.contains("gsrtc.in")) {
            loadTicketUrl(url);
        } else {
            showHomeScreen();
        }
    }

    private void loadTicketUrl(String url) {
        if (!url.startsWith("http://") && !url.startsWith("https://")) {
            url = "https://" + url;
        }

        isViewingTicket = true;
        showWebViewScreen("GSRTC Ticket PDF", true);
        webView.loadUrl(url);
    }

    private void loadWebsiteUrl(String url) {
        isViewingTicket = false;
        showWebViewScreen("GSRTC Portal", false);
        webView.loadUrl(url);
    }

    private void showHomeScreen() {
        panelHome.setVisibility(View.VISIBLE);
        panelWebView.setVisibility(View.GONE);
        btnBack.setVisibility(View.GONE);
        btnPrint.setVisibility(View.GONE);
        txtHeaderTitle.setText("🚍 GSRTC Ticket Fixer");
    }

    private void showWebViewScreen(String title, boolean showPrint) {
        panelHome.setVisibility(View.GONE);
        panelWebView.setVisibility(View.VISIBLE);
        btnBack.setVisibility(View.VISIBLE);
        btnPrint.setVisibility(showPrint ? View.VISIBLE : View.GONE);
        txtHeaderTitle.setText(title);
    }

    private void handleBackNavigation() {
        if (panelWebView.getVisibility() == View.VISIBLE) {
            if (webView.canGoBack()) {
                webView.goBack();
            } else {
                showHomeScreen();
            }
        } else {
            finish();
        }
    }

    private void printTicket() {
        if (webView.getContentHeight() <= 0) {
            Toast.makeText(this, "Please wait for ticket to finish loading.", Toast.LENGTH_SHORT).show();
            return;
        }

        PrintManager printManager = (PrintManager) getSystemService(PRINT_SERVICE);
        if (printManager == null) {
            Toast.makeText(this, "Print service unavailable on this device", Toast.LENGTH_SHORT).show();
            return;
        }

        PrintDocumentAdapter adapter = webView.createPrintDocumentAdapter("GSRTC_Fixed_Ticket");
        PrintAttributes attributes = new PrintAttributes.Builder()
                .setMediaSize(PrintAttributes.MediaSize.ISO_A4)
                .setResolution(new PrintAttributes.Resolution("gsrtc", "GSRTC PDF", 300, 300))
                .setMinMargins(PrintAttributes.Margins.NO_MARGINS)
                .build();

        printManager.print("GSRTC Fixed Ticket", adapter, attributes);
    }

    @Override
    public void onBackPressed() {
        if (panelWebView.getVisibility() == View.VISIBLE) {
            handleBackNavigation();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        handleIncomingIntent(intent);
    }
}
