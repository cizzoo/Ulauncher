pkgname=ulauncher-custom
pkgver=6.0.0_beta27
pkgrel=1
pkgdesc="Feature rich application launcher for Linux (Custom Build)"
arch=('any')
url="https://github.com/cizzoo/Ulauncher"
license=('GPL3')
depends=('gtk3' 'gtk-layer-shell' 'python' 'python-gobject' 'python-cairo' 'python-xlib' 'libnotify')
makedepends=('git' 'python-build' 'python-installer' 'python-wheel' 'python-setuptools')
conflicts=('ulauncher' 'ulauncher-git')
provides=('ulauncher')

source=("ulauncher-src::git+file://${PWD}")
sha256sums=('SKIP')

pkgver() {
  cd "$srcdir/ulauncher-src"
  python -c "import ulauncher; print(ulauncher.version)" | sed 's/-/_/g'
}

build() {
  cd "$srcdir/ulauncher-src"
  python -m build --wheel --no-isolation
}

package() {
  cd "$srcdir/ulauncher-src"
  python -m installer --destdir="$pkgdir" dist/*.whl

  # explicitly install the systemd service
  # -D: create directories if missing
  # -m644: set permissions to read-only (rw-r--r--)
  install -Dm644 ulauncher.service "$pkgdir/usr/lib/systemd/user/ulauncher.service"
}
