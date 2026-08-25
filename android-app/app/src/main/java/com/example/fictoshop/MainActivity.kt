package com.example.fictoshop

import android.annotation.SuppressLint
import android.os.Bundle
import android.view.View
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.ImageButton
import android.widget.LinearLayout
import androidx.activity.ComponentActivity
import androidx.core.view.ViewCompat
import androidx.core.view.updatePadding

class MainActivity : ComponentActivity() {

    private lateinit var webView: WebView
    private lateinit var backButton: ImageButton
    private lateinit var forwardButton: ImageButton
    private lateinit var reloadButton: ImageButton
    private lateinit var navBar: LinearLayout

    @SuppressLint("SetJavaScriptEnabled")
    @Suppress("DEPRECATION") // allow file URLs to reach the API from the bundled asset
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        webView = findViewById(R.id.webview)
        backButton = findViewById(R.id.nav_back)
        forwardButton = findViewById(R.id.nav_forward)
        reloadButton = findViewById(R.id.nav_reload)
        navBar = findViewById(R.id.nav_bar)

        // WebView settings to allow local assets to call remote APIs
        val settings: WebSettings = webView.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.allowFileAccess = true
        settings.allowFileAccessFromFileURLs = true
        settings.allowUniversalAccessFromFileURLs = true

        webView.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                updateNavState()
            }
        }

        backButton.setOnClickListener {
            if (webView.canGoBack()) webView.goBack()
        }
        forwardButton.setOnClickListener {
            if (webView.canGoForward()) webView.goForward()
        }
        reloadButton.setOnClickListener { webView.reload() }

        webView.loadUrl("file:///android_asset/index.html")
        updateNavState()

        // Raise nav bar above content and respect system insets
        navBar.bringToFront()
        ViewCompat.setOnApplyWindowInsetsListener(navBar) { v, insets ->
            val bottomInset = insets.systemWindowInsetBottom
            v.updatePadding(bottom = v.paddingBottom + bottomInset)
            insets
        }
    }

    private fun updateNavState() {
        backButton.isEnabled = webView.canGoBack()
        forwardButton.isEnabled = webView.canGoForward()
        backButton.alpha = if (webView.canGoBack()) 1.0f else 0.35f
        forwardButton.alpha = if (webView.canGoForward()) 1.0f else 0.35f
    }

    override fun onBackPressed() {
        if (this::webView.isInitialized && webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }
}
