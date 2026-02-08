#!/bin/bash

# Function to increment version
increment_version() {
  local delimiter=.
  local array=($(echo "$1" | tr $delimiter '\n'))
  array[2]=$((array[2]+1))
  echo $(local IFS=$delimiter ; echo "${array[*]}")
}

# Current Version
CURRENT_VERSION=$(cat VERSION)
NEW_VERSION=$(increment_version $CURRENT_VERSION)

if [ -n "$1" ]; then
    NEW_VERSION="$1"
fi

echo "Bumping version from $CURRENT_VERSION to $NEW_VERSION"

# Update VERSION file
echo "$NEW_VERSION" > VERSION

# Update Android build.gradle
# Regex to find 'versionName "X.Y.Z"' and replace with 'versionName "NEW_VERSION"'
sed -i "s/versionName \"$CURRENT_VERSION\"/versionName \"$NEW_VERSION\"/" android/app/build.gradle

# Update VersionCode (simple increment)
# extracting current version code
CURRENT_CODE=$(grep "versionCode" android/app/build.gradle | awk '{print $2}')
NEW_CODE=$((CURRENT_CODE + 1))
sed -i "s/versionCode $CURRENT_CODE/versionCode $NEW_CODE/" android/app/build.gradle

echo "Updated files. Creating git tag..."

git add VERSION android/app/build.gradle
git commit -m "Bump version to $NEW_VERSION"
git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION"

echo "Done. Created tag v$NEW_VERSION"
