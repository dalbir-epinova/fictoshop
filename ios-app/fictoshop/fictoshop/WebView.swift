import SwiftUI
import WebKit
import Combine

final class WebViewStore: ObservableObject {
    @Published var canGoBack: Bool = false
    @Published var canGoForward: Bool = false
    let webView: WKWebView = WKWebView(frame: .zero)
}

struct WebView: UIViewRepresentable {
    @ObservedObject var store: WebViewStore

    class Coordinator: NSObject, WKNavigationDelegate {
        private let parent: WebView
        init(parent: WebView) { self.parent = parent }

        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            parent.store.canGoBack = webView.canGoBack
            parent.store.canGoForward = webView.canGoForward
        }

        func webView(_ webView: WKWebView, didCommit navigation: WKNavigation!) {
            parent.store.canGoBack = webView.canGoBack
            parent.store.canGoForward = webView.canGoForward
        }

        func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
            print("WKWebView navigation failed: \(error.localizedDescription)")
        }

        func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
            print("WKWebView provisional navigation failed: \(error.localizedDescription)")
        }
    }

    func makeCoordinator() -> Coordinator { Coordinator(parent: self) }

    func makeUIView(context: Context) -> WKWebView {
        let webView = store.webView
        webView.navigationDelegate = context.coordinator

        if let apiBase = Bundle.main.object(forInfoDictionaryKey: "API_BASE_URL") as? String, !apiBase.isEmpty {
            let escaped = apiBase.replacingOccurrences(of: "\"", with: "\\\"")
            let scriptSource = "window.__FICTO_API_BASE__ = \"\(escaped)\";"
            let script = WKUserScript(source: scriptSource, injectionTime: .atDocumentStart, forMainFrameOnly: true)
            webView.configuration.userContentController.addUserScript(script)
        }

        // Copy bundled mobile-web to a writable temp directory to avoid sandbox extension issues on device.
        if
            let bundleWebFolder = Bundle.main.url(forResource: "mobile-web", withExtension: nil),
            let fileURL = Bundle.main.url(forResource: "index", withExtension: "html", subdirectory: "mobile-web")
        {
            do {
                let html = try String(contentsOf: fileURL, encoding: .utf8)
                // Load HTML as a string with the bundle folder as baseURL to keep requests inside the sandbox.
                webView.loadHTMLString(html, baseURL: bundleWebFolder)
            } catch {
                print("Failed to load mobile-web/index.html: \(error.localizedDescription)")
                webView.loadFileURL(fileURL, allowingReadAccessTo: bundleWebFolder)
            }
        } else {
            assertionFailure("mobile-web/index.html not found in bundle")
        }
        return webView
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {}
}
