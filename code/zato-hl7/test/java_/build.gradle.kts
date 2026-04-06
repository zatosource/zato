plugins {
    java
    application
    id("com.github.johnrengelman.shadow") version "8.1.1"
}

group = "io.zato.hl7"
version = "1.0.0"

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(21))
    }
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("ca.uhn.hapi:hapi-base:2.6.0")
    implementation("ca.uhn.hapi:hapi-structures-v25:2.6.0")
    implementation("ca.uhn.hapi:hapi-structures-v24:2.6.0")
    implementation("ca.uhn.hapi:hapi-structures-v23:2.6.0")

    testImplementation("org.junit.jupiter:junit-jupiter:5.11.4")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher:1.11.4")
}

application {
    mainClass.set("zato.hl7.interop.InteropRunner")
}

tasks.test {
    useJUnitPlatform()
}

tasks.shadowJar {
    archiveBaseName.set("zato-hl7-interop")
    archiveClassifier.set("all")
    archiveVersion.set("")
    mergeServiceFiles()
}
