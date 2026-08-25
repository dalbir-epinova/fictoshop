//
//  ContentView.swift
//  fictoshop
//
//  Created by Dalbir Singh on 01/12/2025.
//

import SwiftUI
import WebKit

struct ContentView: View {
    @StateObject private var store = WebViewStore()

    var body: some View {
        ZStack(alignment: .bottom) {
            WebView(store: store)
                .ignoresSafeArea()

            HStack(spacing: 24) {
                Button(action: { store.webView.goBack() }) {
                    Image(systemName: "chevron.backward")
                        .font(.title3)
                        .frame(width: 44, height: 44)
                        .contentShape(Rectangle())
                }
                .disabled(!store.canGoBack)

                Button(action: { store.webView.reload() }) {
                    Image(systemName: "arrow.clockwise")
                        .font(.title3)
                        .frame(width: 44, height: 44)
                        .contentShape(Rectangle())
                }

                Button(action: { store.webView.goForward() }) {
                    Image(systemName: "chevron.forward")
                        .font(.title3)
                        .frame(width: 44, height: 44)
                        .contentShape(Rectangle())
                }
                .disabled(!store.canGoForward)
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 12)
            .background(.ultraThinMaterial)
            .clipShape(Capsule())
            .padding(.bottom, 16)
            .buttonStyle(.plain)
        }
    }
}
