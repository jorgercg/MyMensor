// Include gulp
var gulp = require('gulp');

// Include Our Plugins
var sass = require('gulp-sass');
var concat = require('gulp-concat');
var rename = require('gulp-rename');
var autoprefixer = require('autoprefixer');
var postcss = require('gulp-postcss');

//Compile our sass
gulp.task('sass', function() {
	return gulp.src('mymensor/static/scss/*.scss')
					.pipe(sass())
					.pipe(gulp.dest('mymensor/static/css'));
});

// Concatenate
gulp.task('scripts', function(){
	return gulp.src('mymensor/static/js/*.js')
					.pipe(concat('all.js'))
					.pipe(gulp.dest('mymensor/static/js'));
});

// PostCSS processor
gulp.task('css', function(){
	var processors = [
		autoprefixer({browsers: ['last 1 version']}),
	];
	return gulp.src('mymensor/static/css/*.css')
					.pipe(postcss(processors))
					.pipe(gulp.dest('mymensor/static/css'))
});

// Watch Files for changes
gulp.task('watch',function(){
	gulp.watch('mymensor/static/js/*.js', ['scripts']);
	gulp.watch('mymensor/static/scss/*.scss', ['sass']);
	gulp.watch('mymensor/static/css/*.css', ['css']);
});

// Default Task
gulp.task('default', ['sass', 'css', 'scripts', 'watch']);