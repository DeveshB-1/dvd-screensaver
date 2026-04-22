import QtQuick 2.15

Rectangle {
    id: root
    color: "black"

    readonly property var colors: [
        "#ff0000", "#00ff00", "#0000ff",
        "#ffff00", "#ff00ff", "#00ffff",
        "#ff8800", "#ffffff"
    ]

    property int colorIdx: 0
    property real logoW: 220
    property real logoH: 90
    property real posX: 0
    property real posY: 0
    property real dx: 3.0
    property real dy: 0.0
    property int bounces: 0
    property int corners: 0
    property real cornerFlash: 0.0

    function initSpeeds() {
        var ew = root.width  - logoW
        var eh = root.height - logoH
        function gcd(a, b) { return b === 0 ? a : gcd(b, a % b) }
        var g = gcd(Math.round(ew), Math.round(eh))
        var speed = 3.0
        root.dx = speed
        root.dy = (eh / g) * speed / (ew / g)
        if (Math.random() < 0.5) root.dx *= -1
        if (Math.random() < 0.5) root.dy *= -1
        root.posX = Math.random() * ew
        root.posY = Math.random() * eh
    }

    function nextColor() {
        var i
        do { i = Math.floor(Math.random() * colors.length) } while (i === colorIdx)
        colorIdx = i
    }

    Component.onCompleted: initSpeeds()

    // DVD logo
    Item {
        x: root.posX
        y: root.posY
        width: root.logoW
        height: root.logoH

        Text {
            text: "DVD"
            font.family: "Arial Black"
            font.pixelSize: 58
            font.weight: Font.Black
            color: root.colors[root.colorIdx]
            x: 0; y: 0
        }

        Rectangle {
            x: 0; y: 74
            width: 130; height: 6
            radius: 3
            color: root.colors[root.colorIdx]
        }

        Text {
            text: "VIDEO"
            font.family: "Arial"
            font.pixelSize: 11
            font.weight: Font.Bold
            color: root.colors[root.colorIdx]
            x: 138; y: 70
            letterSpacing: 1
        }

        Canvas {
            x: 78; y: 2
            width: 64; height: 18
            onPaint: {
                var ctx = getContext("2d")
                ctx.clearRect(0, 0, width, height)
                ctx.strokeStyle = root.colors[root.colorIdx]
                ctx.lineWidth = 1.5
                ctx.beginPath()
                ctx.ellipse(0, 0, width, height)
                ctx.stroke()
            }
            property string watchColor: root.colors[root.colorIdx]
            onWatchColorChanged: requestPaint()
        }
    }

    // corner flash
    Text {
        anchors.centerIn: parent
        text: "CORNER!"
        font.family: "Arial Black"
        font.pixelSize: 64
        font.weight: Font.Black
        color: root.colors[root.colorIdx]
        opacity: Math.min(root.cornerFlash, 1.0)
        visible: root.cornerFlash > 0
    }

    // counters
    Text {
        anchors { bottom: parent.bottom; right: parent.right; margins: 16 }
        text: "BOUNCES: " + root.bounces + "   CORNERS: " + root.corners
        font.family: "Monospace"
        font.pixelSize: 12
        color: "white"
        opacity: 0.25
    }

    Timer {
        interval: 16
        running: true
        repeat: true
        onTriggered: {
            root.posX += root.dx
            root.posY += root.dy

            var hitX = false, hitY = false
            if (root.posX <= 0) {
                root.posX = 0; root.dx = Math.abs(root.dx); hitX = true
            }
            if (root.posX + root.logoW >= root.width) {
                root.posX = root.width - root.logoW; root.dx = -Math.abs(root.dx); hitX = true
            }
            if (root.posY <= 0) {
                root.posY = 0; root.dy = Math.abs(root.dy); hitY = true
            }
            if (root.posY + root.logoH >= root.height) {
                root.posY = root.height - root.logoH; root.dy = -Math.abs(root.dy); hitY = true
            }

            if (hitX || hitY) {
                root.bounces++
                root.nextColor()
                if (hitX && hitY) {
                    root.corners++
                    root.cornerFlash = 1.5
                }
            }

            if (root.cornerFlash > 0)
                root.cornerFlash = Math.max(0, root.cornerFlash - 0.02)
        }
    }
}
