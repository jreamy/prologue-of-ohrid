
load-android:
	mkdir -p ./android/app/src/main/assets
	npx react-native bundle --dev false --platform android --entry-file index.js --bundle-output ./android/app/src/main/assets/index.android.bundle --assets-dest ./android/app/src/main/res
	cd android && ./gradlew clean
	cd android && ./gradlew assembleRelease
	adb install -r ./android/app/build/outputs/apk/release/app-release.apk
