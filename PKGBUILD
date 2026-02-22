# Maintainer: Jude A M <jude@spineguard.dev>
pkgname=spineguard
pkgver=1.0.0
pkgrel=1
pkgdesc='Back health Pomodoro timer with enforced full-screen breaks'
arch=('any')
url='https://github.com/judeam/spineguard'
license=('MIT')
depends=('python' 'python-gobject' 'gtk4')
optdepends=('gsound: sound notifications' 'libappindicator-gtk3: system tray icon')
makedepends=('python-build' 'python-installer' 'python-setuptools' 'python-wheel')
source=("${pkgname}-${pkgver}.tar.gz::${url}/archive/v${pkgver}.tar.gz")
sha256sums=('SKIP')

build() {
    cd "${pkgname}-${pkgver}"
    python -m build --wheel --no-isolation
}

package() {
    cd "${pkgname}-${pkgver}"
    python -m installer --destdir="${pkgdir}" dist/*.whl
    install -Dm644 data/spineguard.desktop "${pkgdir}/usr/share/applications/spineguard.desktop"
    install -Dm644 data/com.spineguard.app.metainfo.xml "${pkgdir}/usr/share/metainfo/com.spineguard.app.metainfo.xml"
    install -Dm644 assets/icon-48.png "${pkgdir}/usr/share/icons/hicolor/48x48/apps/spineguard.png"
    install -Dm644 assets/icon-64.png "${pkgdir}/usr/share/icons/hicolor/64x64/apps/spineguard.png"
    install -Dm644 assets/icon-128.png "${pkgdir}/usr/share/icons/hicolor/128x128/apps/spineguard.png"
    install -Dm644 assets/icon-256.png "${pkgdir}/usr/share/icons/hicolor/256x256/apps/spineguard.png"
    install -Dm644 assets/tray-48.png "${pkgdir}/usr/share/spineguard/tray-icon.png"
    install -Dm644 LICENSE "${pkgdir}/usr/share/licenses/${pkgname}/LICENSE"
}
