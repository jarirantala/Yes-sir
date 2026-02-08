#!/bin/bash
# Verification script for Android build
# Requires JDK 17 or JDK 21

echo "Checking Java version..."
java -version

echo "Building Debug APK..."
./gradlew :app:assembleDebug

if [ $? -eq 0 ]; then
    echo "Build SUCCESS!"
else
    echo "Build FAILED. Please ensure you are using JDK 17 or 21."
fi
