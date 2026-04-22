import QtQuick 2.15

Rectangle {
    id: root
    color: "black"

    readonly property var colors: [
        "#ff3355", "#ff8800", "#ffe600",
        "#00ff88", "#00ccff", "#aa44ff",
        "#ff44cc", "#00ffcc"
    ]

    property int colorIdx: 0
    property real logoW: 220
    property real logoH: 100
    property real posX: 100
    property real posY: 80
    property real dx: 2.5
    property real dy: 1.9
    property int bounces: 0
    property int corners: 0
    property real cornerFlash: 0

    function nextColor() {
        var i
        do { i = Math.floor(Math.random() * colors.length) } while (i === colorIdx)
        colorIdx = i
    }

    // DVD logo
    Item {
        id: logo
        x: root.posX
        y: root.posY
        width: root.logoW
        height: root.logoH

        Text {
            id: dvdText
            text: "DVD"
            font.family: "Arial Black"
            font.pixelSize: 72
            font.weight: Font.Black
            color: root.colors[root.colorIdx]
            x: 4
            y: 0
            style: Text.Outline
            styleColor: "transparent"

            layer.enabled: true
            layer.effect: null
        }

        // underline bar
        Rectangle {
            x: 4
            y: 82
            width: 148
            height: 7
            radius: 3.5
            color: root.colors[root.colorIdx]
        }

        // VIDEO label
        Text {
            text: "VIDEO"
            font.family: "Arial"
            font.pixelSize: 13
            font.weight: Font.Bold
            color: root.colors[root.colorIdx]
            x: 162
            y: 72
            letterSpacing: 2
        }

        // disc ellipse hint
        Canvas {
            x: 80
            y: 4
            width: 80
            height: 22
            onPaint: {
                var ctx = getContext("2d")
                ctx.clearRect(0, 0, width, height)
                ctx.strokeStyle = root.colors[root.colorIdx]
                ctx.lineWidth = 1.5
                ctx.globalAlpha = 0.4
                ctx.beginPath()
                ctx.ellipse(0, 0, width, height)
                ctx.stroke()
            }
            Component.onCompleted: requestPaint()
        }
    }

    // glow behind logo
    Rectangle {
        x: root.posX + root.logoW / 2 - width / 2
        y: root.posY + root.logoH / 2 - height / 2
        width: root.logoW * 1.4
        height: root.logoH * 1.4
        radius: 20
        color: root.colors[root.colorIdx]
        opacity: 0.07
        blur: 40
    }

    // corner flash text
    Text {
        anchors.centerIn: parent
        text: "CORNER!"
        font.family: "Arial Black"
        font.pixelSize: 72
        font.weight: Font.Black
        color: root.colors[root.colorIdx]
        opacity: root.cornerFlash > 0 ? Math.min(root.cornerFlash * 2.5, 1.0) : 0
        visible: root.cornerFlash > 0
    }

    // bounce counter
    Text {
        anchors { bottom: parent.bottom; right: parent.right; margins: 18 }
        text: "BOUNCES: " + root.bounces + "   CORNERS: " + root.corners
        font.family: "Monospace"
        font.pixelSize: 12
        color: "white"
        opacity: 0.2
    }

    // main tick timer
    Timer {
        interval: 16
        running: true
        repeat: true
        onTriggered: {
            root.posX += root.dx
            root.posY += root.dy

            var hitX = false, hitY = false

            if (root.posX <= 0) {
                root.posX = 0
                root.dx = Math.abs(root.dx)
                hitX = true
            }
            if (root.posX + root.logoW >= root.width) {
                root.posX = root.width - root.logoW
                root.dx = -Math.abs(root.dx)
                hitX = true
            }
            if (root.posY <= 0) {
                root.posY = 0
                root.dy = Math.abs(root.dy)
                hitY = true
            }
            if (root.posY + root.logoH >= root.height) {
                root.posY = root.height - root.logoH
                root.dy = -Math.abs(root.dy)
                hitY = true
            }

            if (hitX || hitY) {
                root.bounces++
                root.nextColor()
                if (hitX && hitY) {
                    root.corners++
                    root.cornerFlash = 1.0
                }
            }

            if (root.cornerFlash > 0)
                root.cornerFlash = Math.max(0, root.cornerFlash - 0.016)
        }
    }
}
