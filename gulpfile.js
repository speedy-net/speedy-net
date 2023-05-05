var gulp = require('gulp');
var sass = require('gulp-sass');
var rename = require('gulp-rename');
var rtlcss = require('gulp-rtlcss');

sass.compiler = require('node-sass');

function buildTheme(name) {
    return gulp.src('./themes/' + name + '/index.scss')
        .pipe(sass().on('error', sass.logError))
        .pipe(rename(name + '-ltr.css'))
        .pipe(gulp.dest('./speedy/core/static/themes/'))
        .pipe(rtlcss())
        .pipe(rename(name + '-rtl.css'))
        .pipe(gulp.dest('./speedy/core/static/themes/'));
}

gulp.task('build:speedy-net', function () {
    return buildTheme('speedy-net');
});

gulp.task('build:speedy-match', function () {
    return buildTheme('speedy-match');
});

gulp.task('build', ['build:speedy-net', 'build:speedy-match']);

// gulp.task('watch', function () {
//     return gulp.watch('./themes/**/*', ['build']);
// });

gulp.task('default', ['build']);

