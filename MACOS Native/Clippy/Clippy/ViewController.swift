//
//  ViewController.swift
//  Clippy
//
//  Created by Smil on 26/04/25.
//

import Cocoa
import WebKit
import HotKey

class ViewController: NSViewController {
    @IBOutlet weak var webView: WKWebView!
    var hotkey: HotKey?
    var windowHeightBeforeHide: Double = 100

    override func viewDidAppear() {
        super.viewDidAppear()
        if let window = self.view.window {
            window.level = .screenSaver
            window.collectionBehavior = [
                .canJoinAllSpaces,
                .fullScreenAuxiliary
            ]
           
            var frame = window.frame
            frame.size.height = windowHeightBeforeHide
            frame.size.width = 620
            window.setFrame(frame, display: true, animate: true)
            window.styleMask.remove(.miniaturizable)
            window.styleMask.remove(.resizable)
            window.title = "Clippy"
        }
    }
    
    func changeWindowHeight(height: String) {
        if let window = self.view.window {
            if let heightValue = Double(height) {
                print("changning height to \(heightValue)")
                var frame = window.frame
                frame.size.height = heightValue
                window.setFrame(frame, display: true, animate: true)
                windowHeightBeforeHide = heightValue
            }
        }
    }

    override func observeValue(forKeyPath keyPath: String?, of object: Any?, change: [NSKeyValueChangeKey : Any]?, context: UnsafeMutableRawPointer?) {
        if keyPath == "title" {
            if let newTitle = change?[.newKey] as? String {
                print(newTitle)
                changeWindowHeight(height: newTitle)
            }
        }
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        
        if let url = URL(string: "http://127.0.0.1:8550/") {
            let request = URLRequest(url: url)
            webView.load(request)
        }
        
        webView.addObserver(self, forKeyPath: "title", options: [.old, .new], context: nil)
        
        hotkey = HotKey(key: .space, modifiers: [.command, .control, .option])
        hotkey?.keyDownHandler = { [weak self] in
            guard let window = self?.view.window else {
                print("No window found.")
                return
            }

            if window.isVisible {
                window.orderOut(nil)
            } else {
                
                let oldHeight = self?.windowHeightBeforeHide ?? 100

                print("Restoring height to: \(oldHeight)")

                
                window.makeKeyAndOrderFront(nil)
                
                self?.changeWindowHeight(height: "\(oldHeight)")

                NSApp.activate(ignoringOtherApps: true)
            }
        }
    }

    override var representedObject: Any? {
        didSet {
            // Update the view, if already loaded.
        }
    }
}
