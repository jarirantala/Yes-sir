package com.example.yessir

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.view.MotionEvent
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.livedata.observeAsState
import androidx.compose.ui.Alignment
import androidx.compose.ui.ExperimentalComposeUiApi
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInteropFilter
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.example.yessir.ui.VoiceUiState
import com.example.yessir.ui.VoiceViewModel
import com.example.yessir.ui.ListItemsScreen
import com.example.yessir.ui.components.JSONCard
import com.example.yessir.ui.components.StatusText
import com.google.gson.GsonBuilder
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Menu
import kotlinx.coroutines.launch
import com.example.yessir.constants.NavKeys
import com.example.yessir.ui.VoiceHomeScreen
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    private val viewModel: VoiceViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        setContent {
            MaterialTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    val navController = rememberNavController()
                    val drawerState = rememberDrawerState(initialValue = DrawerValue.Closed)
                    val scope = rememberCoroutineScope()

                    ModalNavigationDrawer(
                        drawerState = drawerState,
                        drawerContent = {
                            ModalDrawerSheet {
                                Spacer(modifier = Modifier.height(16.dp))
                                NavigationDrawerItem(
                                    label = { Text(stringResource(R.string.menu_home)) },
                                    selected = false,
                                    onClick = {
                                        navController.navigate(NavKeys.HOME) {
                                            popUpTo(NavKeys.HOME) { inclusive = true }
                                        }
                                        scope.launch { drawerState.close() }
                                    },
                                    modifier = Modifier.padding(NavigationDrawerItemDefaults.ItemPadding)
                                )
                                NavigationDrawerItem(
                                    label = { Text(stringResource(R.string.tab_todos)) },
                                    selected = false,
                                    onClick = {
                                        navController.navigate("history/0")
                                        scope.launch { drawerState.close() }
                                    },
                                    modifier = Modifier.padding(NavigationDrawerItemDefaults.ItemPadding)
                                )
                                NavigationDrawerItem(
                                    label = { Text(stringResource(R.string.tab_notes)) },
                                    selected = false,
                                    onClick = {
                                        navController.navigate("history/1")
                                        scope.launch { drawerState.close() }
                                    },
                                    modifier = Modifier.padding(NavigationDrawerItemDefaults.ItemPadding)
                                )
                                NavigationDrawerItem(
                                    label = { Text(stringResource(R.string.menu_settings)) },
                                    selected = false,
                                    onClick = {
                                        navController.navigate(NavKeys.SETTINGS)
                                        scope.launch { drawerState.close() }
                                    },
                                    modifier = Modifier.padding(NavigationDrawerItemDefaults.ItemPadding)
                                )
                            }
                        }
                    ) {
                        AppNavigation(
                            navController = navController,
                            viewModel = viewModel,
                            onMenuClick = { scope.launch { drawerState.open() } }
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun AppNavigation(
    navController: androidx.navigation.NavHostController,
    viewModel: com.example.yessir.ui.VoiceViewModel,
    onMenuClick: () -> Unit
) {
    NavHost(navController = navController, startDestination = NavKeys.HOME) {
        composable(NavKeys.HOME) {
            VoiceHomeScreen(
                viewModel = viewModel,
                onMenuClick = onMenuClick
            )
        }
        composable(
            NavKeys.HISTORY,
            arguments = listOf(androidx.navigation.navArgument(NavKeys.INITIAL_TAB) {
                type = androidx.navigation.NavType.IntType
                defaultValue = 0
            })
        ) { backStackEntry ->
            val initialTab = backStackEntry.arguments?.getInt(NavKeys.INITIAL_TAB) ?: 0
            ListItemsScreen(
                viewModel = viewModel,
                initialTab = initialTab,
                onMenuClick = onMenuClick
            )
        }
        composable(NavKeys.SETTINGS) {
            com.example.yessir.ui.SettingsScreen(
                viewModel = viewModel,
                onMenuClick = onMenuClick
            )
        }
    }
}



